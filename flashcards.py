#!/usr/bin/env python3
"""===============================================================================

        FILE: flashcards.py

       USAGE: ./flashcards.py test
              insert word: ./flashcards.py --tags japanese --tags reading add-item "運用" --back "practical use"

 DESCRIPTION:

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION:
     VERSION: 0.0.1
     CREATED: 2020-09-24 11:19 +0900
    REVISION: ---

TODO:
    1(done). type-in question type
    3. `--(no)-hint` key for `test`
    11. key sort order in output, add `deck_index`to `GROUP_BY`
    12. `search` command
    13. test server to use during lunch
    14. different score/selection strategies
    15. log to file always
    17(done). print question asked and change of its score
    18. https://stackoverflow.com/a/2904057
    19. auto-prompt in `_repl_loop`

==============================================================================="""
import click
from pymongo import MongoClient
import pandas as pd
from random import choice
from re import match
import logging
from _flashcards.question import get_question_types, get_question
from _flashcards import get_random_question, get_deck_with_score, GROUP_BY, get_cards
import json
from math import ceil
from os.path import splitext


@click.group()
@click.option("--tags", multiple=True, envvar="TAGS")
@click.option("--debug", is_flag=True)
@click.option("-q", "--question_type", type=click.Choice(get_question_types()), envvar="QUESTION_TYPE")
@click.pass_context
def flashcards(ctx, tags, question_type, debug=False):
    if debug:
        logging.basicConfig(level=logging.INFO)

    ctx.ensure_object(dict)
    ctx.obj["tags"] = tags
    ctx.obj["question_type"] = question_type
    ctx.obj["cards"] = get_cards(tags)


@flashcards.command()
@click.option("--deck-size", type=int, default=5, envvar="DECK_SIZE")
@click.option("--deck-index", type=int, default=-1, envvar="DECK_INDEX")
@click.option("--full/--no-full", default=False)
@click.option("--sort/--no-sort", default=False)
@click.option("--agg", type=click.Choice([*GROUP_BY, "none"]), multiple=True)
@click.pass_context
def show_score(ctx, deck_index, deck_size, full, sort, agg):
    _logger = logging.getLogger("show_score")
    cards = ctx.obj["cards"]
    deck_count = ceil(len(cards)/deck_size)
    _logger.info(f"{deck_count} decks")
    assert deck_index >= -1
    if agg == ("none",):
        agg = []
    elif agg == ():
        agg = GROUP_BY

    deck = []
    for _deck_index in range(deck_count):
        deck.extend([{**card, "deck_index": _deck_index}
                     for card in cards[deck_size*_deck_index:(_deck_index+1)*deck_size]])
    # _logger.info(f"deck: {deck}")
    if deck_index >= 0:
        deck = [card for card in deck if card["deck_index"] == deck_index]
    assert(len(deck) > 0)
    deck = [{k: v for k, v in c.items() if k not in ["tags"]}
            for c in deck]
    _logger.info(f"deck:\n{pd.DataFrame(deck)}")

    deck_df = get_deck_with_score(deck, ctx.obj["question_type"])

    if True:
        deck_df = deck_df.reset_index()
        _all = {"deck_index", *GROUP_BY}
        _agg = list({"deck_index", *agg, })

        def _aggregator(x):
            idx, df = x
            __logger = _logger.getChild("_aggregator")
            return pd.DataFrame([{
                **{k: v for k, v in zip(_agg, idx if len(_agg) > 1 else [idx])},
                **{k: v.mean() if k == "score" else choice(list(v)) for k, v in df.items() if k not in _all},
            }])

        deck_df = pd.concat(map(_aggregator, deck_df.groupby(
            _agg, as_index=False))).reset_index().drop(columns=["index"]).set_index(_agg)

    if not full:
        deck_df = deck_df.drop(columns=["back", "front"])
    else:
        index_names = deck_df.index.names
        deck_df = deck_df.reset_index()
        for i in range(deck_df["back"].apply(len).max()):
            deck_df[f"back[{i}]"] = deck_df["back"].apply(
                lambda back: None if len(back) <= i else back[i])
        deck_df = deck_df.drop(columns=["back"]).set_index(index_names)

    if sort:
        deck_df = deck_df.sort_values(by="score", ascending=False)

    # deck_df = deck_df.drop_duplicates()
    COL_SPACE = 10
    print(deck_df.to_string(justify="left", col_space=COL_SPACE))
    print(f"average score: {deck_df['score'].mean()*100:05.2f}%")


def _repl_loop(callback, prompt):
    while True:
        res, msg = callback(input(f"{prompt}> "))
        if msg is not None:
            print(f"({msg})")
        if res is not None:
            break
    click.echo(click.style(f"res: {res}",
                           fg="green" if res == 1.0 else "red"))
    return res, msg


@flashcards.command()
@click.option("--deck-size", type=int, default=5, envvar="DECK_SIZE")
@click.option("--deck-index", type=int, default=-1, envvar="DECK_INDEX")
@click.option("--allow-regrade/--no-allow-regrade", default=False)
@click.pass_context
def test(ctx, deck_index, deck_size, allow_regrade):
    _logger = logging.getLogger("test")
    cards = ctx.obj["cards"]
    _logger.info(f"{int(len(cards)/deck_size)+1} decks")
    assert deck_index >= 0

    deck = cards[deck_size*deck_index:deck_size*(deck_index+1)]
    deck = [{k: v for k, v in c.items() if k not in ["tags"]}
            for c in deck]
    assert(len(deck) > 0)
    _logger.info(f"deck:\n{pd.DataFrame(deck)}")
    question_i = 0
    while True:
        question_i += 1
        _d = get_random_question(deck, ctx.obj["question_type"])
        question = get_question(
            _d["question_type"], **{k: v for k, v in _d.items() if k != "question_type"})
        print(f"question #{question_i}: \n{question.get_question_text()}")
        res, msg = _repl_loop(question.grade, "answer")

        regrade_text = question.get_regrade_text()
        if regrade_text is not None and allow_regrade and res < 1.0:
            print(regrade_text)
            res, msg = _repl_loop(question.regrade, "regrade")

        obj = json.loads(question.to_json())
        _logger.info(f"obj: {json.dumps(obj, indent=2, sort_keys=True)}")
        MongoClient().alex_flashcards.results.insert_one(obj)
        _PERCENTILES_COUNT = 11
        click.echo((get_deck_with_score(deck, ctx.obj["question_type"])["score"]*100.0).describe(
            percentiles=[i/(_PERCENTILES_COUNT-1) for i in range(1, _PERCENTILES_COUNT-1)]))


@flashcards.command()
@click.argument("front")
@click.option("--back", multiple=True)
@click.pass_context
def add_item(ctx, **kwargs):
    coll = MongoClient().alex_flashcards.cards
    obj = {"tags": ctx.obj["tags"], **kwargs}
    print(f"inserting {obj}")
    coll.insert_one(obj)


@flashcards.command()
@click.argument("filename", type=click.Path())
@click.pass_context
def add_batch(ctx, filename):
    assert splitext(filename)[1] == ".csv", "filename should be a `.csv` file"
    batch = pd.read_csv(filename, sep="\t", header=None)
    coll = MongoClient().alex_flashcards.cards
    back_size = len(list(batch))-1
    batch = pd.DataFrame({"front": batch[0], "back": map(lambda t: [
                         x for x in t if not pd.isna(x)], zip(*[batch[i+1] for i in range(back_size)]))})
    coll.insert_many([{"tags": ctx.obj["tags"], **r}
                      for r in batch.to_dict(orient="records")])


if __name__ == "__main__":
    flashcards()
