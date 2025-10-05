import logging
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from api.models.user import SendMessageResponse, SendToUserRequest
from aiogram import Bot
from fastapi import Depends


router = APIRouter(tags=["User"], prefix="/user")
templates = Jinja2Templates(directory="templates")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def get_bot() -> Bot:
    from bot import bot
    return bot


@router.post("/send-to-user", response_model=SendMessageResponse)
async def send_to_user(
    request: SendToUserRequest,
    bot: Bot = Depends(get_bot)
) -> SendMessageResponse:
    """
    Отправить сообщение конкретному пользователю
    """
    try:
        await bot.send_message(request.user_id, request.text)
        return SendMessageResponse(
            success=True,
            message=f"Сообщение отправлено пользователю {request.user_id}",
            user=request.user_id
        )
    except Exception as e:
        logger.error(f"Ошибка отправки пользователю {request.user_id}: {e}")
        return SendMessageResponse(
            success=False,
            message=f"Ошибка отправки: {str(e)}",
            user=request.user_id
        )