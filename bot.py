from config import Telegram_BOTID
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
import logging


def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Welcome!! I'm still in developing....")


def help(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Help is still in developing....")


def settings(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="For the moment I do not have any settings :)")


def echo(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="You said \n" + update.message.text)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
updater = Updater(token=Telegram_BOTID)
dispatcher = updater.dispatcher

startHandler = CommandHandler(command='start', callback=start)
helpHandler = CommandHandler(command='help', callback=help)
settingsHandler = CommandHandler(command='settings', callback=settings)
echoHandler = MessageHandler(Filters.text, echo)

dispatcher.add_handler(startHandler)
dispatcher.add_handler(helpHandler)
dispatcher.add_handler(settingsHandler)
dispatcher.add_handler(echoHandler)

updater.start_polling()
