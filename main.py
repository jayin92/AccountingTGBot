from dataclasses import replace
import os
import json
import logging

from telegram import CallbackQuery, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters
)

from firebase import writeRecord, getRecord, getTodayRecord
from record import Record

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))

# Different features
AMOUNT, TYPE, NAME, ACCOUNT, COMMENT, FINISH = range(6)


async def cancel(update, context):
    await update.message.reply_text("本筆記帳已取消", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

async def finish(update: Update, context):
    
    logger.info(f"New record by {update.effective_user.full_name}.")
    writeRecord(update.effective_user.id, context.user_data["record"])
    await update.message.reply_text(f"本筆記帳已記錄完畢, 以下為記帳紀錄\n{context.user_data['record']}", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def quick_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ReplyKeyboardRemove()
    reply_keyboard = [["/finish"], ["/skip"], ["/cancel"]]
    context.user_data["record"] = Record(amount=update.message.text, name="", type="", account="default", comment="")
    await update.message.reply_text(
        f'本次記帳金額為 {update.message.text}\n若要取消本次記帳，請輸入 /cancel\n若要跳過名稱輸入，請輸入 /skip\n若要直接完成本次記帳，請輸入 /finish。\n否則，請輸入記帳名稱\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["/finish", "/skip", "/cancel"], ["食物"], ["衣服"], ["交通"], ["日用品"], ["運動"], ["其他"]]
    res = ""
    if update.message.text[0] != "/":
        context.user_data["record"].name = update.message.text
        res += f"本次記帳名稱為 {update.message.text}\n"
    res += "若要取消本次記帳，請輸入 /cancel\n若要跳過類別輸入，請輸入 /skip\n若要直接完成本次記帳，請輸入 /finish。\n否則，請輸入記帳類別\n"
    await update.message.reply_text(
        res,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return TYPE


async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["/finish", "/skip", "/cancel"], ["現金"], ["悠遊卡"]]
    res = ""
    if update.message.text[0] != "/":
        context.user_data["record"].type = update.message.text
        res += f"本次記帳類別為 {update.message.text}\n"
    res += "若要取消本次記帳，請輸入 /cancel\n若要跳過帳戶輸入，請輸入 /skip\n若要直接完成本次記帳，請輸入 /finish。\n否則，請輸入記帳帳戶\n"
    await update.message.reply_text(
        res,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return ACCOUNT




async def account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["/finish"], ["/skip"], ["/cancel"]]
    res = ""
    if update.message.text[0] != "/":
        context.user_data["record"].account = update.message.text
        res += f"本次記帳帳戶為 {update.message.text}\n"
    res += "若要取消本次記帳，請輸入 /cancel\n若要跳過備註輸入，請輸入 /skip\n若要直接完成本次記帳，請輸入 /finish。\n否則，請輸入記帳備註\n"
    await update.message.reply_text(
        res,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return COMMENT


async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    res = ""
    if update.message.text[0] != "/":
        context.user_data["record"].comment = update.message.text
        res += f"本次記帳備註為 {update.message.text}\n"
    res += "若要取消本次記帳，請輸入 /cancel\n若要直接完成本次記帳，請輸入 /finish。"
    await update.message.reply_text(
        res,
        reply_markup=ReplyKeyboardMarkup([["/finish", "/cancel"]], one_time_keyboard=True),
    )

async def check_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["all_records"] = getRecord(update.effective_user.id)[::-1]
    context.user_data["record_idx"] = 0
    keyboard = [
        [InlineKeyboardButton("上一筆", callback_data="prev"), InlineKeyboardButton("下一筆", callback_data="next")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "最近 5 筆記帳紀錄：\n"
    for record in context.user_data["all_records"][context.user_data["record_idx"]:context.user_data["record_idx"] + 5]:
        message += f"{record}\n"
    await update.message.reply_text(message, reply_markup=reply_markup)

async def check_record_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("上一筆", callback_data="prev"), InlineKeyboardButton("下一筆", callback_data="next")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.answer()

    if query.data == "prev":
        if context.user_data["record_idx"] < 5:
            return
        else:
            context.user_data["record_idx"] -= 5
    elif query.data == "next":
        if context.user_data["record_idx"] == len(context.user_data["all_records"]) - 5:
            return
        else:
            context.user_data["record_idx"] += 5
    message = "最近 5 筆記帳紀錄：\n"
    for record in context.user_data["all_records"][context.user_data["record_idx"]:context.user_data["record_idx"] + 5]:
        message += f"{record}\n"
    await query.edit_message_text(text=message, reply_markup=reply_markup)
    
async def check_today_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["today_records"], total = getTodayRecord(update.effective_user.id)
    context.user_data["today_records"] = context.user_data["today_records"][::-1]
    message = "今日記帳紀錄：\n"
    message += f"消費總金額：{total}\n\n"
    for record in context.user_data["today_records"]:
        message += f"{record}\n"
    await update.message.reply_text(message)


async def func_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_description = """
<b>Accounting TG Bot 使用說明</b>
直接輸入金額開始記帳
輸入 /today 查看今天記帳紀錄
輸入 /record 查看最近 5 筆記帳紀錄
輸入 /help 顯示此說明

Developed by @jayinnn
    """
    await update.message.reply_text(help_description, parse_mode="HTML")


def main() -> None:
    with open("secrets.json", "r") as f:
        secrets = json.load(f)

    bot_token = secrets["bot_token"]

    app = ApplicationBuilder().token(bot_token).build()

    quick_exp_handler = ConversationHandler(
        entry_points=[MessageHandler(filters=filters.Regex(r"^[0-9]*$"), callback=quick_expense)],
        states = {
            NAME: [
                CommandHandler("cancel", cancel),
                CommandHandler("finish", finish),
                CommandHandler("skip", name),
                MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=name),
            ],
            TYPE: [
                CommandHandler("cancel", cancel),
                CommandHandler("finish", finish),
                CommandHandler("skip", categories),
                MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=categories)
            ],
            ACCOUNT: [
                CommandHandler("cancel", cancel),
                CommandHandler("finish", finish),
                CommandHandler("skip", account),
                MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=account)
            ],
            COMMENT: [
                CommandHandler("cancel", cancel),
                CommandHandler("finish", finish),
                CommandHandler("skip", finish),
                MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=comment)
            ],

        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )


    app.add_handler(quick_exp_handler)
    app.add_handler(CommandHandler("record", check_record))
    app.add_handler(CommandHandler("today", check_today_record))
    app.add_handler(CommandHandler("help", func_help))
    app.add_handler(CallbackQueryHandler(check_record_button))
    if "ON-HEROKU" in os.environ:
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=bot_token,
            webhook_url="https://jay-accounting-tg-bot.herokuapp.com/" + bot_token
        )
    else:
        app.run_polling()

if __name__ == "__main__":
    main()
