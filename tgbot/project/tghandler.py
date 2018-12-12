# coding: utf-8
from django.conf import settings
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, ConversationHandler, MessageHandler, Filters
import logging
from telegram.ext import CommandHandler

from project.tgbot.models import BotCommand, LastCommand, CANCEL_NAME, SavedPostParameter, SavedUrlParameter

MENU1 = 1
AUTHORIZED_USERS = (148598936, 277766178)


def menu(bot, update):
    user = update.message.from_user
    if user['id'] not in AUTHORIZED_USERS:
        logging.info("Unauthorized %s" % (user['id']))
        return start(bot, update)
    logging.info("Menu of %s: %s" % (user.first_name, update.message.text))
    if update.message.text == CANCEL_NAME:
        SavedPostParameter.objects.filter(tg_user_id=update.message.from_user.id).delete()
        SavedUrlParameter.objects.filter(tg_user_id=update.message.from_user.id).delete()
        LastCommand.objects.filter(tg_user_id=update.message.from_user.id).delete()
        return start(bot, update)

    bc = BotCommand.objects.filter(name=update.message.text).first()
    try:
        if bc:
            lc = LastCommand.objects.filter(tg_user_id=update.message.from_user.id).first()
            if not lc:
                LastCommand.objects.get_or_create(tg_user_id=update.message.from_user.id, command=bc)
            else:
                lc.command = bc
                lc.save()
        else:
            bc = LastCommand.objects.get(tg_user_id=update.message.from_user.id).command
        bc.process(update)
    except Exception as e:
        LastCommand.objects.filter(tg_user_id=update.message.from_user.id).delete()
        SavedPostParameter.objects.filter(tg_user_id=update.message.from_user.id).delete()
        SavedUrlParameter.objects.filter(tg_user_id=update.message.from_user.id).delete()
        response = "Invalid command or service is unavailable"
        update.message.reply_text(response, reply_markup=ReplyKeyboardRemove())
    return MENU1


def cancel(bot, update):
    user = update.message.from_user
    logging.info("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def start(bot, update):
    button_list = [[
        x.name
    ] for x in BotCommand.objects.filter(parent__isnull=True)]
    reply_markup = ReplyKeyboardMarkup(button_list)

    update.message.reply_text('Выберите действие', reply_markup=reply_markup)


def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(token=settings.TELEGRAM_TOKEN)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    start_handler = CommandHandler('start', start)

    updater.start_polling()
    dp = updater.dispatcher
    dp.add_handler(start_handler)
    dp.add_handler(MessageHandler(Filters.text, menu))
    dp.add_error_handler(error)
    updater.start_polling()

    updater.idle()


main()
