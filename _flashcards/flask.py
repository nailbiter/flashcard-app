"""===============================================================================

        FILE: /Users/nailbiter/for/forpython/flashcard-app/_flashcards/flask.py

       USAGE: (not intended to be directly executed)

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: ---
     CREATED: 2020-12-10T21:20:23.994783
    REVISION: ---

==============================================================================="""

from flask import Flask
import os
from _flashcards.question import get_question_types, get_question
from _flashcards import get_random_question, get_deck_with_score, GROUP_BY, get_cards, get_mongo_client
import json

app = Flask(__name__)

class _Settings:
    def __init__(self,fn):
        self._fn = fn
        with open(fn) as f:
            self._obj = json.load(f)

@app.route('/test/<path:fn>')
def test(fn):
    return f'Hello, World!: {fn}'
#    ctx.obj["cards"] = get_cards(ctx.obj["tags"], ctx.obj["mongo_url"])
#    _logger = logging.getLogger("test")
#    cards = ctx.obj["cards"]
#    _logger.info(f"{int(len(cards)/deck_size)+1} decks")
#    assert deck_index >= 0
#
#    deck = cards[deck_size*deck_index:deck_size*(deck_index+1)]
#    deck = [{k: v for k, v in c.items() if k not in ["tags"]}
#            for c in deck]
#    assert(len(deck) > 0)
#    _logger.info(f"deck:\n{pd.DataFrame(deck)}")
#    question_i = 0
#    while True:
#        question_i += 1
#        _d = get_random_question(
#            deck, ctx.obj["question_type"], ctx.obj["mongo_url"])
#        question = get_question(
#            _d["question_type"], **{k: v for k, v in _d.items() if k != "question_type"})
#        print(f"question #{question_i}: \n{question.get_question_text()}")
#        res, msg = _repl_loop(question.grade, "answer")
#
#        regrade_text = question.get_regrade_text()
#        if regrade_text is not None and allow_regrade and res < 1.0:
#            print(regrade_text)
#            res, msg = _repl_loop(question.regrade, "regrade")
#
#        obj = json.loads(question.to_json())
#        _logger.info(f"obj: {json.dumps(obj, indent=2, sort_keys=True)}")
#        get_mongo_client(ctx.obj["mongo_url"]
#                         ).alex_flashcards.results.insert_one(obj)
#        _PERCENTILES_COUNT = 11
#        click.echo((get_deck_with_score(deck, ctx.obj["question_type"], ctx.obj["mongo_url"])["score"]*100.0).describe(
#            percentiles=[i/(_PERCENTILES_COUNT-1) for i in range(1, _PERCENTILES_COUNT-1)]))
