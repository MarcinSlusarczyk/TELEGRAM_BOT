# pip install python-telegram-bot
from telegram.ext import *
import keys
import yfinance as yf
import os
import sys
from datetime import timedelta, datetime
import datetime
import pandas as pd



print('Bot is running!')

# Lets us use the /start command
def start_command(update, context):
    update.message.reply_text('Siemka! to co dziś robimy?')

def help_command(update, context):
    update.message.reply_text('na tą chwilę możesz: '
                              '\n\n  - przywitać się'
                              '\n  - uruchomić alert giełdowy dla wybranej społki\nkomenda: /alert,<NAZWA_SPÓŁKI>,><KURS_MAX>,<KURS_MIN>,<PROCENT>'
                              )

def bot_stock(update, context):
    stock_param = update.message.text
    info = stock_param.split(",")
    name = f"alert proces {info[1]}"
    YAHOO_COMPANY = yf.Ticker(info[1])


    try:
        rekomendacja = YAHOO_COMPANY.info["recommendationKey"]
    except:
        rekomendacja = "DATA NO FOUND!"


    update.message.reply_text(f'{YAHOO_COMPANY.info["longName"]} informacje:\n\n'
    f'Recommendation: {rekomendacja}\n\n'
    f'---------STOCK DATA----------\n'
    f'Current price: {YAHOO_COMPANY.info["currentPrice"]}\n'
    f'targetMedianPrice: {YAHOO_COMPANY.info["targetMedianPrice"]}\n'
    f'targetLowPrice: {YAHOO_COMPANY.info["targetLowPrice"]}\n'
    f'targetHighPrice: {YAHOO_COMPANY.info["targetHighPrice"]}\n'
    f'targetMeanPrice: {YAHOO_COMPANY.info["targetMeanPrice"]}\n'
    f'--------------------------------------------\n\n')

    def bot_stock_info(context):

        info = stock_param.split(",")
        COMPANY = info[1]
        TARGET_STOCK_UP = float(info[2])
        TARGET_STOCK_DOWN = float(info[3])
        TARGET_PERCENT = float(info[4])

        YAHOO_COMPANY = yf.Ticker(COMPANY)
        CURRENT_STOCK = float(YAHOO_COMPANY.info["currentPrice"])
        OPEN_STOCK = float(YAHOO_COMPANY.info["open"])
        PERCENT = (CURRENT_STOCK / OPEN_STOCK - 1) * 100

        print(f"ALERT URUCHOMIONY -- {COMPANY} -- CURRENT STOCK: {CURRENT_STOCK} -- CHANGE %: {PERCENT} -- time: {datetime.datetime.now()}")

        if CURRENT_STOCK > TARGET_STOCK_UP:
            text = update.message.reply_text(f' ALERT! KURS WZRÓSŁ \n\n'
                                      f'{YAHOO_COMPANY.info["longName"]} \n'
                                      f'aktualny kurs: {CURRENT_STOCK}\n'
                                      f'zmiana: {PERCENT}\n'
                                      )
            context.bot.send_message(context.job.context, text=text)
            to_remove = context.job_queue.get_jobs_by_name(name)
            to_remove[0].schedule_removal()


        if CURRENT_STOCK < TARGET_STOCK_DOWN:
            text = (f' ALERT! KURS SPADŁ \n'
                                      f'{YAHOO_COMPANY.info["longName"]} \n\n'
                                      f'aktualny kurs: {CURRENT_STOCK}\n'
                                      f'zmiana: {PERCENT}\n'
                                      )
            context.bot.send_message(context.job.context, text=text)
            to_remove = context.job_queue.get_jobs_by_name(name)
            to_remove[0].schedule_removal()

        if PERCENT > TARGET_PERCENT:
            text = (f' ALERT! ZMIANA PROCENTOWA WZROSŁA o {PERCENT}  \n\n'
                                      f'{YAHOO_COMPANY.info["longName"]} \n'
                                      f'aktualny kurs: {CURRENT_STOCK}\n'
                                      f'zmiana: {PERCENT}\n'
                                      )
            context.bot.send_message(context.job.context, text=text)
            to_remove = context.job_queue.get_jobs_by_name(name)
            to_remove[0].schedule_removal()

        if PERCENT < -TARGET_PERCENT:
            text = (f' ALERT! ZMIANA PROCENTOWA SPADŁA o {PERCENT}  \n\n'
                                      f'{YAHOO_COMPANY.info["longName"]} \n'
                                      f'aktualny kurs: {CURRENT_STOCK}\n'
                                      f'zmiana: {PERCENT}\n'
                                      )
            context.bot.send_message(context.job.context, text=text)
            to_remove = context.job_queue.get_jobs_by_name(name)
            to_remove[0].schedule_removal()

    hour_start = datetime.time(7, 0, 0)
    hour_last = datetime.time(15, 16, 0)

    context.job_queue.run_repeating(bot_stock_info, 5, first=hour_start, last=hour_last, context=update.message.chat.id, name=name)


def parking(update, context):
    info = update.message.text
    name = "PARKING"
    def parking_time(context):
        date = info.split(" ")[1] + " 12:00:00"

        date_now = datetime.datetime.now()
        day_date = pd.to_datetime(date).isoweekday()

        if int(day_date) == 1:
            EndDate = pd.to_datetime(date) - timedelta(days=5, hours=12)
        elif int(day_date) == 2:
            EndDate = pd.to_datetime(date) - timedelta(days=5, hours=12)
        elif int(day_date) == 3:
            EndDate = pd.to_datetime(date) - timedelta(days=5, hours=12)
        elif int(day_date) == 4:
            EndDate = pd.to_datetime(date) - timedelta(days=3, hours=12)
        elif int(day_date) == 5:
            EndDate = pd.to_datetime(date) - timedelta(days=3, hours=12)

        context.bot.send_message(context.job.context, text=f"{str(EndDate)[:-3]}")
        day_date_now = pd.to_datetime(date_now)

        if str(day_date_now)[:-10] == str(EndDate)[:-3]:
            context.bot.send_message(context.job.context, text="ZAREZERWUJ PARKING W APCE!!\n\n Usuwam alert!")
            to_remove = context.job_queue.get_jobs_by_name(name)
            to_remove[0].schedule_removal()

    context.job_queue.run_repeating(parking_time, 5, context=update.message.chat.id, name=name)


def handle_message(update, context):

    text = str(update.message.text).lower()

    if text in ('hello', 'cześć', 'hej'):
        update.message.reply_text("No cześć!")
        return text

    elif text in ('jak leci?', 'co tam?'):
        update.message.reply_text("Wszystko ok! ")
        return text

    else:
        update.message.reply_text("Nie rozumiem co napisałeś :(")

# Log errors
def error(update, context):
    print(f'Update {update} powód błędu {context.error}')


def exit(update, context):
    update.message.reply_text("Wyłączam Bota")
    os.execl(sys.executable, sys.executable, *sys.argv)


# Run the program
if __name__ == '__main__':

    updater = Updater(keys.token, use_context=True)
    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('pomoc', help_command))
    dp.add_handler(CommandHandler('alert', bot_stock))
    dp.add_handler(CommandHandler('exit', exit))
    dp.add_handler(CommandHandler('parking', parking))

    # Messages
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()