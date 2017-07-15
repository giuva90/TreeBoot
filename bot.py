#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import configparser
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from copy import deepcopy
import logging
import logging.handlers
from decisionTreeSupport import init, convert

import xml.etree.ElementTree as ET

tree = ET.parse('config.xml')
root = tree.getroot()
Telegram_BOTID = root.find('telegramBotid').text
AdminPassword = root.find('adminPassword').text
datasets = {}
for ds in root.findall('dataset'):
	name = ds.get('name')
	datasets[name] = {}
	datasets[name]['dataset_name'] = ds.find('filename').text
	datasets[name]['class_column'] = int(ds.find('classColumn').text)
	datasets[name]['data_columns'] = [int(x) for x in ds.find('dataColumns').text.split(',')]
del tree, root

# exludedSections = ['TOKENS', 'DEFAULT']
# config = configparser.ConfigParser()
# config.read('configuration.ini')
# config.sections()
# Telegram_BOTID = config['TOKENS']['telegram_botid']
# AdminPassword = config['TOKENS']['admin_password']
# datasets = {}
# for k in config.keys():
# 	if k not in datasets and k not in exludedSections:
# 		# noinspection PyBroadException
# 		try:
#
# 		except:
# 			continue


CHOOSINGTREE, INTERACT = range(2)
LOG_FILENAME = 'logs.log'
treeData = {}
availableClassifierName = []
logging.basicConfig(filename=LOG_FILENAME, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=20000000, backupCount=5))

from botFunctions import *

def start(bot, update):
	message = "Ciao, e benvenuto!"
	message += "\nSono ancora in sviluppo, ecco la lista dei comandi attualmente disponibili:" \
	           "\n/exploretree  Inizia ad esplorare gli alberi" \
	           "\n/help mostra la lista dei comandi disponibili"

	bot.send_message(chat_id=update.message.chat_id, text=message)


def startInteraction(bot, update, chat_data):
	chat_data = {}
	reply_keyboard = []
	for k in availableClassifierName:
		reply_keyboard.append([k])
	reply_keyboard.append(['/cancel'])

	update.message.reply_text('Ciao, scegli cosa vuoi che indovini.\n\n /cancel se vuoi terminare! ',
	                          reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
	return INTERACT


def interactionManager(bot, update, chat_data):
	chose = update.message.text
	if chose in treeData:
		chat_data['chose'] = chose
		return interact(bot, update, chat_data, chose)
	elif 'chose' in chat_data:
		return interact(bot, update, chat_data, chat_data['chose'])
	else:
		bot.send_message(chat_id=update.message.chat_id, text="Scusa, ma non credo di disporre di questo dato...")
		return startInteraction(bot, update, chat_data)


def interact(bot, update, chat_data, chose):
	# Retrieve the data dictionary for tree interactionManager
	if chose in chat_data:
		data = chat_data[chose]
	else:
		data = deepcopy(treeData[chose])
		chat_data[chose] = data
		chat_data['step'] = 1  # 1 = ask question, 0 = process answer
	dt = treeData['dt' + chose]

	while not data['__stop']:
		toAsk = data['toAsk']
		if data['step'] == 1:
			if 'valueRange' in toAsk:
				# IF the feature has numeric value within an interval:
				if chat_data['step']:
					question = data['questions'][toAsk['feature']] + "Range: " + str(toAsk['valueRange'])
					update.message.reply_text(question, reply_markup=ReplyKeyboardRemove())
					return INTERACT
				else:
					user_value_for_feature = convert(update.message.text.strip())
				if toAsk['valueRange'][0] <= user_value_for_feature <= toAsk['valueRange'][1]:
					data['step'] = 0
					data['s'][toAsk['feature']] = user_value_for_feature
					data = dt.classify_by_asking_questions(data['actualNode'], data)
				else:
					question = data['questions'][toAsk['feature']] + "Range: " + str(toAsk['valueRange'])
					update.message.reply_text(question, reply_markup=ReplyKeyboardRemove())
					return INTERACT
			elif 'possibleAnswer' in toAsk:
				# If the features has a symbolic value
				if chat_data['step']:
					if 'featuresHumanization' in data and toAsk['feature'] in data['featuresHumanization']:
						reply_keyboard = [[str(x) for x in data['featuresHumanization'][toAsk['feature']]]]
					else:
						reply_keyboard = [[str(x) for x in toAsk['possibleAnswer']]]
					update.message.reply_text(data['questions'][toAsk['feature']],
					                          reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
					chat_data['step'] = 0
					return INTERACT
				else:
					if 'featuresHumanization' in data and toAsk['feature'] in data['featuresHumanization']:
						user_value_for_feature = convert(data['featuresHumanization'][toAsk['feature']]
						                                 .index(update.message.text.strip()))
					else:
						user_value_for_feature = convert(update.message.text.strip())
					if user_value_for_feature in toAsk['possibleAnswer']:
						data['step'] = 0
						data['toAsk']['givenAnswer'] = user_value_for_feature
						data = dt.classify_by_asking_questions(data['actualNode'], data)
						chat_data['step'] = 1
					else:
						if 'featuresHumanization' in data and toAsk['feature'] in data['featuresHumanization']:
							reply_keyboard = [[str(x) for x in data['featuresHumanization'][toAsk['feature']]]]
						else:
							reply_keyboard = [[str(x) for x in toAsk['possibleAnswer']]]
						update.message.reply_text("Valore non valido!\n" + data['questions'][toAsk['feature']],
						                          reply_markup=ReplyKeyboardMarkup(reply_keyboard,
						                                                           one_time_keyboard=True))
						return INTERACT
		else:
			logger.critical("Sono finito in uno stato morto...")
			del chat_data['Animals'], data
			update.message.reply_text(
				"Perdona, mi sono rotto un braccio! devo scappare in ospedale :("
				"\nTi lascio con mio fratello, ma devi ricominciare.",
				reply_markup=ReplyKeyboardRemove())
			return ConversationHandler.END

	message = "Ottimo! Ho trovato qualcosa!\n"
	classification = data['a']
	del classification['solution_path']
	which_classes = list(classification.keys())
	which_classes = sorted(which_classes, key=lambda x: classification[x], reverse=True)
	if classification[which_classes[0]] < 1:
		message += "\nEcco la probabilità delle risposte, io sceglierei la prima ;)\n"
		message += "\n     " + str.ljust("Classe", 30) + "Probabilità"
		message += "\n     ----------                    -----------"
		for which_class in which_classes:
			if which_class is not 'solution_path' and classification[which_class] > 0:
				message += "\n     " + str.ljust(which_class, 30) + str(round(classification[which_class], 2))
	else:
		if 'singleAnswer' in data['interaction']:
			message += data['interaction']['singleAnswer'] + '\n'
		else:
			message += "\n\nSai cosa?, sono quasi sicuro che la risposta corretta sia "
		if str(which_classes[0][5:]) in data['classHumanization']:
			message += data['classHumanization'][str(which_classes[0][5:])]
		else:
			message += str(which_classes[0])

	message += "\nCosa vuoi fare?"
	reply_keyboard = [['Ricomincia', 'Esci'], ]  # ['Valuta la classificazione']]
	update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	del chat_data[chose], data, chat_data['chose']
	return CHOOSINGTREE


def main():
	for name, v in datasets.items():
		logging.info("Start training tree " + name)
		data = init(v['dataset_name'], v['class_column'], v['data_columns'])
		treeData['dt' + name] = deepcopy(data['dt'])
		del data['dt']
		treeData[name] = deepcopy(data)
		# data['actualNode'].display_decision_tree("   ")
		del data
		logging.info("End training tree " + name)

	for k in treeData.keys():
		if not k.startswith('dt'):
			availableClassifierName.append(k)

	logging.info("Bot Starting...!")

	updater = Updater(token=Telegram_BOTID)
	dispatcher = updater.dispatcher

	startHandler = CommandHandler(command='start', callback=start)
	helpHandler = CommandHandler(command='help', callback=help)
	settingsHandler = CommandHandler(command='settings', callback=settings)
	adminIdentify = CommandHandler(command=AdminPassword, callback=imAdmin, pass_chat_data=True)
	serverInfo = CommandHandler(command='getIP', callback=getServerInfo, pass_chat_data=True)

	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('exploretree', startInteraction, pass_chat_data=True)],

		states={
			INTERACT: [  # RegexHandler('^(Animals)$', interactionManager, pass_chat_data=True),
				MessageHandler(Filters.text, interactionManager, pass_chat_data=True)],
			CHOOSINGTREE: [RegexHandler('^(Ricomincia)$', startInteraction, pass_chat_data=True),
			               RegexHandler('^(Esci)$', cancel, pass_chat_data=True),
			               RegexHandler('^(Valuta la classificazione)$', tbd, pass_chat_data=True)]
		},

		fallbacks=[CommandHandler('cancel', cancel, pass_chat_data=True),
		           MessageHandler(Filters.command, unknown)]
	)

	# echoHandler = MessageHandler(Filters.text, echo)
	unknownCommandHandler = MessageHandler(Filters.command, unknown)

	dispatcher.add_handler(adminIdentify)
	dispatcher.add_handler(serverInfo)
	dispatcher.add_handler(startHandler)
	dispatcher.add_handler(helpHandler)
	dispatcher.add_handler(settingsHandler)
	dispatcher.add_handler(conv_handler)
	# dispatcher.add_handler(echoHandler)

	dispatcher.add_handler(unknownCommandHandler)
	dispatcher.add_error_handler(error)
	updater.start_polling()
	logging.info("Bot Started!")
	print("Bot Started correctly!")
	updater.idle()


if __name__ == '__main__':
	main()
