import mysql.connector
import logging
from aiogram import Bot, Dispatcher, executor, types, exceptions
import asyncio
import schedule
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def update_telegram_ids():
    cnx = mysql.connector.connect(
        host="xxx",
        user="xxx",
        password="xxx",
        database="xxx"
    )
    cursor = cnx.cursor()

    update_query = "UPDATE v2_user SET telegram_id = SUBSTRING_INDEX(email, '@', 1) WHERE email LIKE '%@%' AND telegram_id IS NULL"

    try:
        cursor.execute(update_query)
        cnx.commit()
        logger.info("Telegram IDs updated successfully")
    except Exception as e:
        logger.error(f"Error occurred during update: {str(e)}")
        cnx.rollback()

    cursor.close()
    cnx.close()

def job():
    update_telegram_ids()

schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
