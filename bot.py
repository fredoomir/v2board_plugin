#!/usr/bin/env python

import logging
import requests
from telegram import __version__ as TG_VER
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from panel import Panel
from utils import load_config, get_timestamp
import argparse
import datetime
import random
from math import ceil
import yaml



# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("BOT")
async def is_member(update: Update, context: ContextTypes.DEFAULT_TYPE, send_thank_you=True):
    config = load_config(config_path)
    # Check if the client is a member of the specified channel
    user_id = update.effective_user.id # update.message.from_user.id  # Get the client's user ID
    try:
        chat_member = await context.bot.get_chat_member(chat_id=config["telegram_channel_id"], user_id=user_id)
        if chat_member.status in ["member", "creator"]:
            if send_thank_you:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you for subscribing to our channel!")
        else:
            message = f" کاربر گرامی {update.effective_user.username} عزیز\n\n" \
              "من به شما پیشنهاد می‌کنم حتماً در کانال عضو شوید و سپس دوباره امتحان کنید. در این کانال، شما قادر خواهید بود آموزش‌ها و آپدیت‌های جدید را دریافت کنید و از فروش کانفیگ‌های رایگان جلوگیری کنید"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            await context.bot.send_message(chat_id=update.effective_chat.id, text="https://t.me/womanlifefreedom13")
            
        return chat_member.status in ["member", "creator"]
    except:
        logger.error(f"Error in checking the members of the channel. Please make sure robot is admin to your channel {config['telegram_channel_id']}")
        return False

async def is_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    config = load_config(config_path)
    if config['maintenance']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry. The bot is under maintanance right now.")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="ما در حال حاضر در حال ارتقا ربات هستیم و به طور موقت ربات غیر فعال شده است.")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="در حال حاضر سرور پر شده است. ")

    return config['maintenance']

async def gen_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    maintenance = await is_maintenance(update, context)
    if maintenance:
        return
        
    if not update.effective_user.username:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please setup a username for your telegram account.")
        return

    if not await is_member(update, context, send_thank_you=False):
        return

    print(f"Gave link to {str(update.effective_user.username)}")
    config = load_config(config_path)
    item = panel.search_user_by_email_prefix(str(update.effective_user.id),page_size=150)
    if item:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="شما قبلا اشتراک اختصاصی #نیکا_شاکرمی  خود را دریافت کرده اید.\n\n لینک اشتراک اختصاصی شما:\n\n ")
        sub_url = item['subscribe_url']
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"<code>{sub_url}</code>", parse_mode="HTML")
    else:
        result, message = panel.add_user(str(update.effective_user.id), str(update.effective_user.username), get_timestamp(config['expiry_days']),config['default_user_password'],plan_id=config['plan_id'])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    
        result, sub_url = panel.get_sub(str(update.effective_user.id), str(update.effective_user.username))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"<code>{sub_url}</code>", parse_mode="HTML")
        
    text = f"لطفاً روزانه لینک سابسکرایب را در نرم افزار خود به‌روز کنید.\n\nاشتراک #نیکا_شاکرمی تنها در نرم افزارهایی که در بخش آموزش مشخص شده، قابل استفاده است. \n\n-لطفاً از کانال خارج نشوید؛ زیرا در صورت خروج، اشتراک شما بلاک خواهد شد. این اقدام به منظور جلوگیری از فروش غیرقانونی اشتراک‌های رایگان است. \n\nکانال آموزش\n\nhttps://t.me/iFreedom13\n\n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    maintenance = await is_maintenance(update, context)
    if maintenance:
        return

    keyboard = [[InlineKeyboardButton("دریافت اشتراک اختصاصی #نیکا_شاکرمی ۱۳ گیگ ", callback_data="gen_link")],
                [InlineKeyboardButton("گزارش استفاده از حجم اشتراک🪫", callback_data="usage")],[InlineKeyboardButton("Apple id: ShadowRocket🚀", callback_data="appleid")],[InlineKeyboardButton("آموزش iOS", callback_data="ios"),InlineKeyboardButton("آموزش اندرويد", callback_data="android")],[InlineKeyboardButton("پشتیبانی ⛑", callback_data="note")],[InlineKeyboardButton(" تست سرعت🚄", web_app=WebAppInfo(url="https://pcmag.speedtestcustom.com"))]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("با افتخار آماده خدمت رسانی به شما هستیم، لطفا یک گزینه انتخاب کنید:", reply_markup=reply_markup)
    
async def gen_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_config(config_path)
    result, usage = panel.get_usage(str(update.effective_user.id))
    usage = float(usage)
    usage_rounded = ceil(usage)     # تبدیل به عدد بالاترین
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"مقدار مصرفی شما: \n {usage_rounded} GB\n\n ♻️حجم ترافیک  اشتراک شما در ۱۳ هر ماه  به صورت خودکار ریست می شود.")

    
async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = f"\n\n{update.effective_chat.id}@{update.effective_user.username}\n\n\n\n لطفا اول کانال آموزش بررسی کنید، اگر همچنان مشکل در ارتباط داشتید این پیام را به همراه شرح کامل مشکل و ورژن نرم افزار و اینترنت خودتون برای  ربات پشتیبان ارسال کنید.\n\n https://t.me/womanlifefreedom13Support_bot\n\n"
    await  context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")
    
async def ios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = f"آموزش استفاده از لینک اشتراک در iOS؛ \n\nV2box:\n\nhttps://t.me/iFreedom13/42\n\nFoxray:\n\nhttps://t.me/iFreedom13/45\n\nShadow Rocket\n\nhttps://t.me/iFreedom13/47\n\n"
    await  context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")
    
async def android(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = f"آموزش استفاده از لینک اشتراک در اندروید؛ \n\nV2rayNG:\n\nحتما دقت کنید ورژن نرم افزار بالا تر از ۱.۸.۱ باشه در غیر این صورت نرم افزار پاک کنید و دوباره دانلود و نصب کنید.\n\nhttps://t.me/iFreedom13/28\n\n"
    await  context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")



async def appleid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    maintenance = await is_maintenance(update, context)
    if maintenance:
        return
        
    if not update.effective_user.username:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please setup a username for your telegram account.")
        return

    if not await is_member(update, context, send_thank_you=False):
        return

    print(f"Gave link to {str(update.effective_user.username)}")
    config = load_config(config_path)
    item = panel.search_user_by_email_prefix(str(update.effective_user.id),page_size=150)
    if item:
     def load_from_yaml(file_path):
         with open(file_path, 'r') as file:
             data = yaml.safe_load(file)
         return data
# مسیر فایل YAML
    file_path = 'data.yaml'
# بارگیری اطلاعات از فایل YAML
    data = load_from_yaml(file_path)
    apple_id = data.get('apple_id')
    apple_id_password = data.get('apple_id_password')
    message = f"apple_id: {apple_id}\n\n\napple_id_password: {apple_id_password}"
    
    await  context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")
    await  context.bot.send_message(chat_id=update.effective_chat.id, text="🚨هشدار!\n\nقبل از استفاده از Apple ID، ویدیو آموزشی نحوه استفاده از آن را ببینید. تمام مسئولیت استفاده ناصحیح یا نادرست از این روش با خودتان است.  \n\n- اعتبار پسورد دریافت شده همان لحطه است، در صورتی که رمز نا معتبر بود ساعتی دیگر دوباره در خواست رمز عبور کنید.\n\n- توجه کنید گه این اپل ایدی تحت مالکیت مانیست پس نمی توانیم در زمان مشکل -اسنفاده نادرست- به شما کمک کنیم")
    video_link = "https://t.me/iFreedom13/38"
    message = f" ویدیو آموزشی: \n<a href='{video_link}'>&#8203;</a>"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="HTML")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()
    if query.data == "gen_link":
        await context.bot.send_message(chat_id=query.message.chat_id, text="🔄 در حال برقراری ارتباط با سرور... لطفاً صبور باشید.")
        await gen_link(update, context)
    elif query.data == "usage":
        await gen_report(update, context)
    elif query.data == "appleid":
        await appleid(update, context)
    elif query.data == "note":
        await note(update, context)
    elif query.data == "ios":
        await ios(update, context)
    elif query.data == "android":
        await android(update, context)
def main() -> None:
    # Parse the config file path from the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path', help='Path to the config file', default='config.yaml')
    args = parser.parse_args()
    global config_path
    config_path = args.config_path
    global panel
    # Load the config file
    config = load_config(config_path)
    panel = Panel(**config['panel'])

    
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config['telegram_bot_token']).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

