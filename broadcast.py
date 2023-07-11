import mysql.connector
import logging
from aiogram import Bot, Dispatcher, executor, types, exceptions
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bot = Bot(token="xxxxx:xxxxxxxx")

async def send_message_to_users(channel, group_id, message):
    cnx = mysql.connector.connect(
        host="xxx",
        user="xxx",
        password="xxx",
        database="xxx"
    )
    cursor = cnx.cursor()

    query = "SELECT telegram_id FROM v2_user WHERE group_id = %s"
    cursor.execute(query, (group_id,))
    results = cursor.fetchall()

    for result in results:
        telegram_id = result[0]
        try:
            await bot.send_message(telegram_id, message)
            logger.info(f"Message sent to user: {telegram_id}")
        except exceptions.BotBlocked:
            logger.error(f"The bot is blocked by user: {telegram_id}")
        except exceptions.ChatNotFound:
            logger.error(f"User {telegram_id} is not found or the bot is not a member of the chat.")
        except exceptions.RetryAfter as e:
            logger.error(f"Sending message to {telegram_id} is limited. Retry after {e.timeout} seconds.")
        except exceptions.UserDeactivated:
            logger.error(f"User {telegram_id} is deactivated.")
        except exceptions.TelegramAPIError as e:
            logger.error(f"Error occurred while sending message to {telegram_id}: {str(e)}")

    cursor.close()
    cnx.close()

async def main():
    channel = -xxxx
    group_id = 13
    message ="pm"
    
#"درود،\n\n با توجه به اتمام حجم اشتراک  حدود ۴۰ ٪ از کاربران لطفا قبل از ارسال پیام به پشتیبانی از ربات مقدار باقی مانده خود را چک کنید، چنانچه مقدار مصرفی ۱۳ و یا ۱۴ گیگ را به شما نشان داد حجم شما تمام شده و باید تا ۱۳ ماه میلادی منتظر شارژ بمانید.\n\n اگر از اول امکان اتصال نداشتید، نرم افزار خود راپاک کنید و دوباره نصب کنید.\n\n ربات ۱۰ دقیقه به علت ارسال پیام غیر فعال است."

    await send_message_to_users(channel, group_id, message)

asyncio.run(main())
