#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from config import Telegram_BOTID
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from copy import deepcopy
import logging
import logging.handlers
from treeAnimals import init, convert

CHOOSINGTREE, INTERACT = range(2)
LOG_FILENAME = 'logs.log'
treeData = {}
logging.basicConfig(filename=LOG_FILENAME, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=2000, backupCount=5))


def error(bot, update, error):
	logger.error('Update "%s" caused error "%s"' % (update, error))


def start(bot, update):
	message = "Ciao, e benvenuto!"
	message += "\nSono ancora in sviluppo, ecco la lista dei comandi attualmente disponibili:" \
	           "\n/exploretree  Inizia ad esplorare gli alberi" \
	           "\n/help mostra la lista dei comandi disponibili"

	bot.send_message(chat_id=update.message.chat_id, text=message)


def help(bot, update):
	message = "Ciao, ecco la lista dei miei comandi\n /exploretree  Inizia ad esplorare gli alberi"
	bot.send_message(chat_id=update.message.chat_id, text=message)


def tbd(bot, update, chat_data):
	message = "Questo funzionalità è ancora in sviluppo!"
	update.message.reply_text(chat_id=update.message.chat_id, text=message, reply_markup=ReplyKeyboardRemove())
	return CHOOSINGTREE


def settings(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="For the moment I do not have any settings :)")


# def echo(bot, update):
# 	bot.send_message(chat_id=update.message.chat_id, text="You said \n" + update.message.text)


def unknown(bot, update):
	bot.send_message(chat_id=update.message.chat_id,
	                 text="Perdona, ma non ho capito il comando.\n /help per avere maggiori info sui comandi disponibili", )


def startInteraction(bot, update, chat_data):
	chat_data = {}
	reply_keyboard = [['Animals', '/cancel']]
	update.message.reply_text('Ciao, scegli cosa vuoi che indovini.\n\n /cancel se vuoi terminare! ',
	                          reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
	return INTERACT


def cancel(bot, update, chat_data):
	user = update.message.from_user
	logger.warn("User %s canceled the conversation." % user.first_name)
	update.message.reply_text('Ciao, spero di rivederti presto!',
	                          reply_markup=ReplyKeyboardRemove())
	if 'Animals' in chat_data:
		del chat_data['Animals']
	return ConversationHandler.END


def InteractAnimals(bot, update, chat_data):
	# Retrieve the data dictionary for tree interaction
	if 'Animals' in chat_data:
		data = chat_data['Animals']
	else:
		data = deepcopy(treeData['Animals'])
		chat_data['Animals'] = data
		chat_data['step'] = 1  # 1 = ask question, 0 = process answer
	dt = treeData['dtAnimals']

	while not data['__stop']:
		toAsk = data['toAsk']
		print("while")
		if data['step'] == 1:
			if 'valueRange' in toAsk:
				if chat_data['step']:
					question = data['questions'][toAsk['feature']] + "Range: " + str(toAsk['valueRange'])
					update.message.reply_text(question, reply_markup=ReplyKeyboardRemove())
				# Se la featuere ha valore numerico compreso in un intervallo:
				user_value_for_feature = input(
					"\nWhat is the value for the feature '" + toAsk['feature'] + "'?" + "\n" +
					"Enter a value in the range: " + str(toAsk['valueRange']) + " => ")
				user_value_for_feature = convert(user_value_for_feature.strip())
				if toAsk['valueRange'][0] <= user_value_for_feature <= toAsk['valueRange'][1]:
					data['step'] = 0
					data['s'][toAsk['feature']] = user_value_for_feature
					data = dt.classify_by_asking_questions(data['actualNode'], data)
				else:
					print("Value not valid!")
					continue
			elif 'possibleAnswer' in toAsk:
				# se la feature ha valore simbolico
				if chat_data['step']:
					# print(toAsk['possibleAnswer'])
					reply_keyboard = [[str(x) for x in toAsk['possibleAnswer']]]
					# print(reply_keyboard)
					update.message.reply_text(data['questions'][toAsk['feature']],
					                          reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
					chat_data['step'] = 0
					return INTERACT
				else:
					user_value_for_feature = convert(update.message.text.strip())
					if user_value_for_feature in toAsk['possibleAnswer']:
						data['step'] = 0
						data['toAsk']['givenAnswer'] = user_value_for_feature
						data = dt.classify_by_asking_questions(data['actualNode'], data)
						chat_data['step'] = 1
					else:
						reply_keyboard = [toAsk['possibleAnswer']]
						update.message.reply_text("Valore non valido!\n" + data['questions'][toAsk['feature']],
						                          reply_markup=ReplyKeyboardMarkup(reply_keyboard,
						                                                           one_time_keyboard=True))
						return INTERACT
		else:
			logger.critical("Sono finito in uno stato morto...")
			del chat_data['Animals'], data
			return ConversationHandler.END
	logger.info("Ho finito, ho trovato una o più classi")
	message = "Ottimo! Ho trovato qualcosa!"
	classification = data['a']
	del classification['solution_path']
	which_classes = list(classification.keys())
	which_classes = sorted(which_classes, key=lambda x: classification[x], reverse=True)
	if classification[which_classes[0]] < 1:
		message += "\n\nEcco la probabilità delle risposte, io sceglierei la prima ;)\n"
		message += "\n     " + str.ljust("Classe", 30) + "Probabilità"
		message += "\n     ----------                    -----------"
		for which_class in which_classes:
			if which_class is not 'solution_path' and classification[which_class] > 0:
				message += "\n     " + str.ljust(which_class, 30) + str(round(classification[which_class], 2))
	else:
		message += "\n\nSai cosa?, sono quasi sicuro che la risposta corretta sia " + str(which_classes[0])

	message += "\nCosa vuoi fare?"
	reply_keyboard = [['Ricomincia', 'Esci'], ['Valuta la classificazione']]
	update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))


	del chat_data['Animals'], data
	return CHOOSINGTREE


def main():
	logging.info("Start training tree")
	data = init("zoo_1.csv", 18, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17])
	treeData['dtAnimals'] = data['dt']
	del data['dt']
	treeData['Animals'] = data
	# data['actualNode'].display_decision_tree("   ")
	logging.info("End training tree")
	logging.info("Bot Started!")
	updater = Updater(token=Telegram_BOTID)
	dispatcher = updater.dispatcher

	startHandler = CommandHandler(command='start', callback=start)
	helpHandler = CommandHandler(command='help', callback=help)
	settingsHandler = CommandHandler(command='settings', callback=settings)

	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('exploretree', startInteraction, pass_chat_data=True)],

		states={
			INTERACT: [  # RegexHandler('^(Animals)$', InteractAnimals, pass_chat_data=True),
				MessageHandler(Filters.text, InteractAnimals, pass_chat_data=True)],
			CHOOSINGTREE: [RegexHandler('^(Ricomincia)$', startInteraction, pass_chat_data=True),
			               RegexHandler('^(Esci)$', cancel, pass_chat_data=True),
			               RegexHandler('^(Valuta la classificazione)$', tbd, pass_chat_data=True)]
		},

		fallbacks=[CommandHandler('cancel', cancel, pass_chat_data=True),
		           MessageHandler(Filters.command, unknown)]
	)

	# echoHandler = MessageHandler(Filters.text, echo)
	unknownCommandHandler = MessageHandler(Filters.command, unknown)

	dispatcher.add_handler(startHandler)
	dispatcher.add_handler(helpHandler)
	dispatcher.add_handler(settingsHandler)
	dispatcher.add_handler(conv_handler)
	# dispatcher.add_handler(echoHandler)

	dispatcher.add_handler(unknownCommandHandler)
	dispatcher.add_error_handler(error)
	updater.start_polling()
	print("Bot Started correctly!")
	updater.idle()


if __name__ == '__main__':
	main()
