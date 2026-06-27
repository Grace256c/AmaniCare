"""USSD menu flow handler for Africa's Talking."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import validate_age, validate_phone_number
from app.models.session import USSDFlow
from app.models.user import LifeStage
from app.repositories.ussd_session_repository import USSDSessionRepository
from app.services.deepseek_service import DeepseekService
from app.services.registration_service import RegistrationService
from app.services.sms_service import AfricaTalkingSMSService

# Africa's Talking response prefixes.
CON = "CON "
END = "END "

LIFE_STAGE_MENU = "\n".join(
    [
        "Choose life stage:",
        "1 Teen",
        "2 Regular",
        "3 TryingToConceive",
        "4 Pregnant",
        "5 Postpartum",
        "6 Perimenopause",
        "7 Menopause",
    ]
)

LIFE_STAGE_MAP: dict[str, LifeStage] = {
    "1": LifeStage.TEEN,
    "2": LifeStage.REGULAR,
    "3": LifeStage.TRYING_TO_CONCEIVE,
    "4": LifeStage.PREGNANT,
    "5": LifeStage.POSTPARTUM,
    "6": LifeStage.PERIMENOPAUSE,
    "7": LifeStage.MENOPAUSE,
}


"""USSD menu flow handler for Africa's Talking."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.security import validate_age, validate_phone_number
from app.models.session import USSDFlow
from app.models.user import LifeStage
from app.repositories.ussd_session_repository import USSDSessionRepository
from app.services.deepseek_service import DeepseekService
from app.services.registration_service import RegistrationService
from app.services.sms_service import AfricaTalkingSMSService
from app.repositories.sms_message_repository import SMSMessageRepository
from app.repositories.user_repository import UserRepository

# Africa's Talking response prefixes.
CON = "CON "
END = "END "

LIFE_STAGE_MENU = "\n".join(
    [
        "Choose life stage:",
        "1 Teen",
        "2 Regular",
        "3 TryingToConceive",
        "4 Pregnant",
        "5 Postpartum",
        "6 Perimenopause",
        "7 Menopause",
    ]
)

LIFE_STAGE_MAP: dict[str, LifeStage] = {
    "1": LifeStage.TEEN,
    "2": LifeStage.REGULAR,
    "3": LifeStage.TRYING_TO_CONCEIVE,
    "4": LifeStage.PREGNANT,
    "5": LifeStage.POSTPARTUM,
    "6": LifeStage.PERIMENOPAUSE,
    "7": LifeStage.MENOPAUSE,
}


class USSDService:
    """Processes Africa's Talking USSD webhook requests."""

    WELCOME_MENU = (
        "Welcome to MamaCare AI\n"
        "1 Register\n"
        "2 Ask Health Question"
    )

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.session_repo = USSDSessionRepository(db)
        self.registration_service = RegistrationService(db)
        self.deepseek_service = DeepseekService()
        self.sms_service = AfricaTalkingSMSService()

    async def handle(
        self,
        *,
        session_id: str,
        phone_number: str,
        text: str,
    ) -> str:
        """Route USSD input to the appropriate menu handler."""
        logger.info(
            "USSD request: session={} phone={} text={!r}",
            session_id,
            phone_number,
            text,
        )

        normalized_phone = self._normalize_phone(phone_number)
        parts = text.split("*") if text else []

        session = await self.session_repo.get_by_session_id(session_id)
        if session is None:
            session = await self.session_repo.create(
                session_id=session_id,
                phone_number=normalized_phone,
            )

        if not parts:
            await self.session_repo.update(session, flow=USSDFlow.MAIN, last_input=text)
            return f"{CON}{self.WELCOME_MENU}"

        main_choice = parts[0]

        if main_choice == "1":
            response = await self._handle_registration(normalized_phone, parts, session)
        elif main_choice == "2":
            response = await self._handle_health_question(normalized_phone, parts, session)
        else:
            response = f"{END}Invalid option. Please dial again."

        return response

    async def _handle_registration(
        self,
        phone_number: str,
        parts: list[str],
        session,
    ) -> str:
        """Multi-step registration flow via USSD."""
        if len(parts) == 1:
            await self.session_repo.update(session, flow=USSDFlow.REGISTER_NAME)
            return f"{CON}Enter your name:"

        if len(parts) == 2:
            name = parts[1].strip()
            if not name:
                return f"{CON}Name cannot be empty. Enter your name:"
            await self.session_repo.update(
                session,
                flow=USSDFlow.REGISTER_AGE,
                temp_name=name,
            )
            return f"{CON}Enter your age:"

        if len(parts) == 3:
            try:
                age = int(parts[2].strip())
                validate_age(age)
            except ValueError:
                return f"{CON}Invalid age. Enter a number between 10 and 120:"

            await self.session_repo.update(
                session,
                flow=USSDFlow.REGISTER_LIFE_STAGE,
                temp_age=age,
            )
            return f"{CON}{LIFE_STAGE_MENU}"

        if len(parts) == 4:
            stage_choice = parts[3].strip()
            life_stage = LIFE_STAGE_MAP.get(stage_choice)
            if life_stage is None:
                return f"{CON}Invalid choice.\n{LIFE_STAGE_MENU}"

            # store life stage and prompt for SMS opt-in
            await self.session_repo.update(
                session,
                flow=USSDFlow.REGISTER_SMS_OPTIN,
                temp_life_stage=life_stage.value,
            )
            return f"{CON}Would you like SMS reminders?\n1 Yes\n2 No"

        if len(parts) == 5:
            opt = parts[4].strip()
            if opt not in ("1", "2"):
                return f"{CON}Invalid choice.\nWould you like SMS reminders?\n1 Yes\n2 No"

            sms_opt_in = opt == "1"

            name = session.temp_name or parts[1].strip()
            age = session.temp_age or int(parts[2].strip())
            life_stage_value = session.temp_life_stage or parts[3].strip()
            life_stage = LIFE_STAGE_MAP.get(life_stage_value) if isinstance(life_stage_value, str) else life_stage_value

            user = await self.registration_service.register_from_ussd(
                phone_number=phone_number,
                name=name,
                age=age,
                life_stage=life_stage,
                sms_opt_in=sms_opt_in,
            )

            # log and send welcome SMS if opted-in
            sms_repo = SMSMessageRepository(self.db)
            template = "welcome"
            # dedupe: do not send welcome twice within 24h
            recent = await sms_repo.has_recent_message(user_id=user.id, template_name=template)
            if sms_opt_in and not recent:
                message = (
                    "Welcome to MamaCare AI. You are now registered for personalized women's health support. Reply STOP anytime to opt out."
                )
                await sms_repo.log_message(
                    phone_number=phone_number,
                    message_body=message,
                    direction="outbound",
                    template_name=template,
                    user_id=user.id,
                )
                # send via SMS service (best-effort, do not block)
                try:
                    sms = AfricaTalkingSMSService()
                    ok = await sms.send_sms(phone_number, message)
                    if ok:
                        user.last_sms_sent_at = datetime.utcnow()
                        await self.registration_service.repo.update(user)
                except Exception:
                    logger.exception("Failed to send welcome SMS for {}", phone_number)

            await self.session_repo.delete(session)
            logger.info("USSD registration complete for {}", phone_number)
            return f"{END}Registration complete. Thank you, {name}!"

        return f"{END}Invalid registration input. Please dial again."

    async def _handle_health_question(
        self,
        phone_number: str,
        parts: list[str],
        session,
    ) -> str:
        """Health question flow: collect question, call Deepseek, return advice."""
        if len(parts) == 1:
            await self.session_repo.update(session, flow=USSDFlow.ASK_QUESTION)
            return f"{CON}Enter your health question:"

        if len(parts) == 2:
            question = parts[1].strip()
            if len(question) < 3:
                return f"{CON}Question too short. Please describe your concern:"

            user = await self.registration_service.get_user(phone_number)
            if user is None:
                await self.session_repo.delete(session)
                return f"{END}You are not registered. Dial again and choose 1 to register."

            try:
                advice = await self.deepseek_service.generate_advice(user, question)
            except ValueError as exc:
                logger.error("Deepseek error during USSD for {}: {}", phone_number, exc)
                await self.session_repo.delete(session)
                return f"{END}Sorry, we could not generate advice right now. Please try again later."
            except Exception as exc:
                logger.error("Unexpected USSD advice error for {}: {}", phone_number, exc)
                await self.session_repo.delete(session)
                return f"{END}Sorry, something went wrong. Please try again later."

            truncated = advice[:600] + "..." if len(advice) > 600 else advice

            # send follow-up SMS summary if user opted in
            try:
                sms_repo = SMSMessageRepository(self.db)
                template = "advice_followup"
                recent = await sms_repo.has_recent_message(user_id=user.id, template_name=template)
                if getattr(user, "sms_opt_in", False) and not recent:
                    summary = f"MamaCare Summary:\n{truncated}"
                    await sms_repo.log_message(
                        phone_number=phone_number,
                        message_body=summary,
                        direction="outbound",
                        template_name=template,
                        user_id=user.id,
                    )
                    sms = AfricaTalkingSMSService()
                    ok = await sms.send_sms(phone_number, summary)
                    if ok:
                        user.last_sms_sent_at = datetime.utcnow()
                        await self.registration_service.repo.update(user)
            except Exception:
                logger.exception("Failed to send follow-up SMS for {}", phone_number)

            await self.session_repo.delete(session)
            return f"{END}{truncated}"

        return f"{END}Invalid input. Please dial again."

    @staticmethod
    def _normalize_phone(phone_number: str) -> str:
        """Normalize Africa's Talking phone numbers to E.164."""
        cleaned = phone_number.strip().replace(" ", "")
        if not cleaned.startswith("+"):
            cleaned = f"+{cleaned.lstrip('+')}"
        return validate_phone_number(cleaned)
