#!/usr/bin/env python3
"""===============================================================================

        FILE: flashcards_server.py

       USAGE: ./flashcards_server.py

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: 0.0.1
     CREATED: 2020-10-05T15:28:00.019712
    REVISION: ---
    
TODO:
    0. remove all FIXMEs
    1. click in selection questions, not type
    3. rewrite into bot (maybe, integrate into `flashcards.py`)

==============================================================================="""
from os import environ
import click
import logging
from pymongo import MongoClient
from re import match
import pandas as pd
from _flashcards import get_random_question, get_cards
from _flashcards.question import get_question_types, get_question
import pickle
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.keyboardbutton import KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
#from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

_QUESTION_PICKLE_FILENAME = ".question.pickle"


def test(update, context):
    deck_size, deck_index, tags = (
        environ[k] for k in ["DECK_SIZE", "DECK_INDEX", "TAGS"])
    tags = [tags]
    deck_size, deck_index = (int(s) for s in [deck_size, deck_index])
    _logger = logging.getLogger("test")

    cards = get_cards(tags)

    _logger.info(f"{int(len(cards)/deck_size)+1} decks")
    assert deck_index >= 0

    deck = cards[deck_size*deck_index:deck_size*(deck_index+1)]
    deck = [{k: v for k, v in c.items() if k not in ["tags"]}
            for c in deck]
    assert(len(deck) > 0)
    _logger.info(f"deck:\n{pd.DataFrame(deck)}")

    question_i = 0  # FIXME
    question_i += 1
    _d = get_random_question(deck)
    question = get_question(
        _d["question_type"], **{k: v for k, v in _d.items() if k != "question_type"})

    with open(_QUESTION_PICKLE_FILENAME, "wb") as f:
        pickle.dump(question, f)

    # return render_template("test.jinja.html",question_text=question.get_question_text(),question_i=question_i)
    _reply_text_kwargs = {"text": question.get_question_text()}
    answer_options = question.get_answer_options()
    if answer_options is not None:
        _HOW_MANY_COLUMNS = 2
        _reply_text_kwargs["reply_markup"] = ReplyKeyboardMarkup(
            [list(map(KeyboardButton, answer_options[i:i+_HOW_MANY_COLUMNS])) for i in range(0, len(answer_options), _HOW_MANY_COLUMNS)], one_time_keyboard=True)
    update.message.reply_text(**_reply_text_kwargs)


def check_answer(update, context):
    _logger = logging.getLogger("check_answer")
    with open(_QUESTION_PICKLE_FILENAME, "rb") as f:
        question = pickle.load(f)
    res, msg = question.grade(update.message.text)

    # FIXME: implement this
#    if msg is not None:
#        print(f"({msg})")
#    if res is not None:
#        break

#    click.echo(click.style(f"res: {res}",
#                           fg="green" if res == 1.0 else "red"))
    # FIXME: output deck score

    if res is not None:
        obj = json.loads(question.to_json())
        _logger.info(f"obj: {json.dumps(obj, indent=2, sort_keys=True)}")
        MongoClient().alex_flashcards.results.insert_one(obj)
    #return render_template("check_answer.jinja.html", res=res, msg=msg)
    _msg = ""
    if msg is not None:
        _msg = f"({msg})"
    update.message.reply_text(f"{res} {_msg}")


@click.command()
@click.option("-t", "--telegram-token", envvar="TELEGRAM_TOKEN")
def main(telegram_token):
    assert telegram_token is not None
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(telegram_token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('test', test))
    updater.dispatcher.add_handler(MessageHandler(
        filters=Filters.all, callback=check_answer))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
