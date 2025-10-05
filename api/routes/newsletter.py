import logging
from fastapi import APIRouter
from sqlalchemy.orm import Session
from api.models.user import SendMessageResponse, SendToUserRequest
from aiogram import Bot
from fastapi import Depends
from database.crud import broadcast_message_sync
from database.db_helper import get_db

router = APIRouter(tags=["User"], prefix="/user")

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


@router.post("/broadcast")
def broadcast_message(
    text: str,
    db: Session = Depends(get_db)
):
    """
    Массовая рассылка сообщений всем пользователям
    """
    return broadcast_message_sync(db, text)




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