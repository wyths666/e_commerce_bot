import logging

from aiogram import Bot
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.crud import broadcast_message_sync
from database.db_helper import get_db

router = APIRouter(prefix="/user", tags=["User"])
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

@router.get("/broadcast", response_class=HTMLResponse)
async def broadcast_page(request: Request):
    return templates.TemplateResponse("broadcast.html", {"request": request})

@router.post("/broadcast")
def broadcast_message(
    request: Request,
    text: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        result = broadcast_message_sync(db, text)
        return templates.TemplateResponse("broadcast.html", {
            "request": request,
            "message": result.get("message", "Рассылка завершена"),
            "success": result.get("success", False)
        })
    except Exception as e:
        logger.error(f"Ошибка при рассылке: {e}")
        return templates.TemplateResponse("broadcast.html", {
            "request": request,
            "message": "Ошибка сервера",
            "success": False
        })

async def get_bot() -> Bot:
    from bot import bot
    return bot

