#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
from bot import CHOOSINGTREE, logger, ConversationHandler, ReplyKeyboardRemove, availableClassifierName
from requests import get


def error(bot, update, error):
	logger.error('Update "%s" caused error "%s"' % (update, error))


def imAdmin(bot, update, chat_data):
	user = update.message.from_user
	logger.info("User %s Has been marked as ADMIN." % user.name)
	chat_data['isAdmin'] = True
	bot.send_message(chat_id=update.message.chat_id,
	                 text="Questa chat è stata marchiata come isAdmin (almeno fino al riavvio del bot)")


def getServerInfo(bot, update, chat_data):
	user = update.message.from_user
	logger.info("User %s Is asking for ServerIP." % user.name)
	if 'isAdmin' in chat_data:
		nmyIP = get('http://ipinfo.io/ip').text
		message = "IP: " + nmyIP
	else:
		message = "Hey Giovane, mi sa che mi stai chiedendo troppo...."
	bot.send_message(chat_id=update.message.chat_id, text=message)



def help(bot, update):
	message = "Ciao, ecco la lista dei miei comandi\n /exploretree  Inizia ad esplorare gli alberi"
	bot.send_message(chat_id=update.message.chat_id, text=message)


def tbd(bot, update, chat_data):
	user = update.message.from_user
	logger.debug("User %s Is asking fo a not developed function." % user.name)
	message = "Questo funzionalità è ancora in sviluppo!"
	update.message.reply_text(chat_id=update.message.chat_id, text=message, reply_markup=ReplyKeyboardRemove())
	return CHOOSINGTREE


def settings(bot, update):

	bot.send_message(chat_id=update.message.chat_id, text="For the moment I do not have any settings :)")

def unknown(bot, update):
	user = update.message.from_user
	logger.debug("User %s typed an unknown command : %s." % user.name, update.message.text)
	bot.send_message(chat_id=update.message.chat_id,
	                 text="Perdona, ma non ho capito il comando.\n /help per avere maggiori info sui comandi disponibili", )


def cancel(bot, update, chat_data):
	user = update.message.from_user
	logger.debug("User %s canceled the conversation." % user.name)
	update.message.reply_text('Ciao, spero di rivederti presto!',
	                          reply_markup=ReplyKeyboardRemove())
	for k in availableClassifierName:
		if k in chat_data:
			del chat_data[k]
	if 'choose' in chat_data:
		del chat_data['choose']
	if 'conversationHistory' in chat_data:
		del chat_data['conversationHistory']

	return ConversationHandler.END
