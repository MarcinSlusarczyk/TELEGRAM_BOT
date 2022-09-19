# pip install python-telegram-bot
from telegram.ext import *
import keys
import time
import yfinance as yf
from threading import Thread

print('Bot is running!')

class AddDaemon(object):
    def __init__(self):
        self.stuff = 'hi there this is AddDaemon'

# Lets us use the /start command
def start_command(update, context):
    update.message.reply_text('Siemka! to co dziś robimy?')

def help_command(update, context):
    update.message.reply_text('na tą chwilę możesz: '
                              '\n\n  - przywitać się'
                              '\n  - musze dodać nowe funkcje do bota'
                              )


def handle_response(text) -> str:
    # Create your own response logic

    if text in ('hello', 'cześć', 'hej'):
        return 'Siemka! mogę coś dla Ciebie sprawdzić / zrobić?'

    elif text in ('jak leci?', 'co tam?'):
        return 'a ogólnie wszystko ok!'

    else:
        return 'nie rozumiem tego co napisałeś'

def handle_message(update, context):
    # Get basic info of the incoming message
    message_type = update.message.chat.type
    text = str(update.message.text).lower()
    response = ''
    # React to group messages only if users mention the bot directly
    response = handle_response(text)

    # Reply normal if the message is in private
    update.message.reply_text(response)


# Log errors
def error(update, context):
    print(f'Update {update} powód błędu {context.error}')

COMPANY_NAME, PRICE_UP, PRICE_DOWN, PERCENT_CHANGE, STATUS = range(5)
user_data = {}


def stock_alert(update, context, status):
    COMPANY = list(user_data.values())[0]
    TARGET_STOCK_UP = float(list(user_data.values())[1])
    TARGET_STOCK_DOWN = float(list(user_data.values())[2])
    TARGET_PERCENT = float(list(user_data.values())[3])

    while status:
        YAHOO_COMPANY = yf.Ticker(COMPANY)
        STOCK = float(YAHOO_COMPANY.info["currentPrice"])
        OPEN_STOCK = float(YAHOO_COMPANY.info["open"])
        PERCENT = (STOCK / OPEN_STOCK - 1) * 100

        if update.message.text in "stop":
            break


        if TARGET_STOCK_UP < STOCK or TARGET_PERCENT < PERCENT:

            update.message.reply_text(f' ALERT! KURS WZRÓSŁ \n'
                                      f'{YAHOO_COMPANY.info["longName"]} \n'
                                      f'aktualny kurs: {STOCK}\n'
                                      f'zmiana: {PERCENT}\n'
                                      )
            break

        if TARGET_STOCK_DOWN > STOCK or (-TARGET_PERCENT) < PERCENT:

            update.message.reply_text(f' ALERT! KURS SPADŁ \n'
                                      f'{YAHOO_COMPANY.info["longName"]} \n'
                                      f'aktualny kurs: {STOCK}\n'
                                      f'zmiana: {PERCENT}\n'
                                      )
            break
        time.sleep(3)


def alert(update, context):
    update.message.reply_text("Witaj w kreatorze alertu! \n\nNajpierw podaj Nazwę społki")
    return COMPANY_NAME

def company_name(update, context):
    user_data[COMPANY_NAME] = update.message.text
    YAHOO_COMPANY = yf.Ticker(update.message.text)
    # print(YAHOO_COMPANY.info)
    update.message.reply_text(f'{YAHOO_COMPANY.info["longName"]} informacje:\n\n'
                              f'Recommendation: {YAHOO_COMPANY.info["recommendationKey"]}\n\n'
                              f'---------STOCK DATA----------\n'
                              f'Current price: {YAHOO_COMPANY.info["currentPrice"]}\n'
                              f'targetMedianPrice: {YAHOO_COMPANY.info["targetMedianPrice"]}\n'
                              f'targetLowPrice: {YAHOO_COMPANY.info["targetLowPrice"]}\n'
                              f'targetHighPrice: {YAHOO_COMPANY.info["targetHighPrice"]}\n'
                              f'targetMeanPrice: {YAHOO_COMPANY.info["targetMeanPrice"]}\n'
                              f'--------------------------------------------\n\n'
                              )
    update.message.reply_text("Podaj górny próg ceny")
    return PRICE_UP


def price_up(update, context):
    user_data[PRICE_UP] = update.message.text
    update.message.reply_text("Podaj dolny próg ceny")
    return PRICE_DOWN

def price_down(update, context):
    user_data[PRICE_DOWN] = update.message.text
    update.message.reply_text("Wskaż zmiane procentową")
    return PERCENT_CHANGE

def percent_change(update, context):
    user_data[PERCENT_CHANGE] = update.message.text
    update.message.reply_text("To już wszystkie pytania!\n\nczy chcesz uruchomić alert?\nwpisz: tak/nie")
    return STATUS

def send_status(update, context):
    user_data[STATUS] = update.message.text
    if user_data[STATUS].lower() == 'tak':
        update.message.reply_text("Alert giełdowy uruchomiony!")
        status = True

        p1 = Thread(target=stock_alert(update, context, status))
        p1.start()
        return ConversationHandler.END

    else:
        update.message.reply_text("Alert giełdowy anulowany!")
        return ConversationHandler.END

def cancel_alert(update, context):
    update.message.reply_text("Wychodzę z alertu!")
    return ConversationHandler.END


# Run the program
if __name__ == '__main__':
    updater = Updater(keys.token, use_context=True)
    dp = updater.dispatcher

    stock_conv = ConversationHandler(
        entry_points=[CommandHandler("alert", alert)],
        states={
            COMPANY_NAME: [MessageHandler(Filters.text, callback=company_name)],
            PRICE_UP: [MessageHandler(Filters.text, callback=price_up)],
            PRICE_DOWN: [MessageHandler(Filters.text, callback=price_down)],
            PERCENT_CHANGE: [MessageHandler(Filters.text, callback=percent_change)],
            STATUS: [MessageHandler(Filters.text, callback=send_status)]
        },
        fallbacks=[CommandHandler("cancel", cancel_alert)],

    )

    # Commands
    dp.add_handler(stock_conv)
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('pomoc', help_command))

    # Messages
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()