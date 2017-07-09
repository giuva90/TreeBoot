from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)


def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Welcome!! I'm still in developing....")


def help(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Help is still in developing....")


def settings(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="For the moment I do not have any settings :)")


def echo(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="You said \n" + update.message.text)


def unknown(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def startInteraction(bot, update):
	reply_keyboard = [['Animals', '/cancel']]
	update.message.reply_text('Ciao, scegli cosa vuoi che indovini.\n\n /cancel se vuoi terminare! ',
	                          reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
	return INTERACT


def cancel(bot, update):
	user = update.message.from_user
	logger.info("User %s canceled the conversation." % user.first_name)
	update.message.reply_text('Ciao, spero di rivederti presto!',
	                          reply_markup=ReplyKeyboardRemove())
	return ConversationHandler.END


def interact(bool, update, chat_data):
	return ConversationHandler.END
