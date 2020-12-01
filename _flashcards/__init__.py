import logging
import pandas as pd
from random import choice, choices
from re import match
from pymongo import MongoClient
from itertools import product
import json
from _flashcards.question import get_question_types, get_question
GROUP_BY = ["_id", "is_front_to_back", "back_index"]
_HISTORY_SIZE = 5


def _compute_slice_score(slice_df):
    return slice_df.sort_values(by="answer_time", ascending=False)["score"][:_HISTORY_SIZE].min()

def add_logger(f):
    logger = logging.getLogger(f.__name__)

    def _f(*args, **kwargs):
        return f(*args, logger=logger, **kwargs)
    return _f


@add_logger
def get_deck_with_score(deck, question_type, mongo_url, logger):
    deck_df = pd.DataFrame(deck)
    deck_df["_id"] = deck_df["_id"].apply(str)
    deck_df = pd.concat([
        pd.DataFrame([{**r, "back_index": back_index, "is_front_to_back": is_front_to_back}
                      for back_index, is_front_to_back in product(range(len(r["back"])), [True, False])])
        for r
        in deck_df.to_dict(orient="records")
    ]).set_index(GROUP_BY)

    results_df = pd.DataFrame(get_mongo_client(mongo_url).alex_flashcards.results.find())
    if len(results_df)==0:
        deck_df["score"] = 0.0
        return deck_df
    results_df = results_df[[tag == question_type for tag in results_df.TAG]]
    results_df["_id"] = results_df["card"]
    results_df.drop(columns=["card"])
    if len(results_df) > 0:
        results_df = pd.DataFrame([
            {
                **{k: v for k, v in zip(GROUP_BY, idx)},
                "score": _compute_slice_score(_df),
            }
            for idx, _df
            in results_df.groupby(GROUP_BY)
        ])
    # print(results_df)
    results_df = results_df.set_index(GROUP_BY)
    _logger.info(f"results_df: {results_df}")

    deck_df = deck_df.join(results_df, how="left")
    deck_df["score"] = deck_df["score"].apply(
        lambda x: 0.0 if pd.isna(x) else x)
    _logger.info(f"deck_df: {deck_df}")
    return deck_df


def get_random_question(deck, question_type, mongo_url):
    _logger = logging.getLogger("get_random_question")
    deck_df = get_deck_with_score(deck, question_type, mongo_url).reset_index()
    records = deck_df.to_dict(orient="records")
    max_weight = 1.0 if (
        min(map(lambda r: r["score"], records)) < 1.0) else 2.0
    record = choices(records, weights=[max_weight-r["score"]
                                       for r in records],  k=1)[0]
    card = next(card for card in deck if str(card["_id"]) == record["_id"])
    is_front_to_back = record["is_front_to_back"]
    back_index = record["back_index"]

    #question_type = choice(get_question_types())
    return {
        "deck": deck,
        "card": card,
        "is_front_to_back": is_front_to_back,
        "back_index": back_index,
        "question_type": question_type
    }


def get_mongo_client(mongo_url):
    return MongoClient(*([] if mongo_url is None else [mongo_url]))


def get_cards(tags, mongo_url):
    coll = get_mongo_client(mongo_url).alex_flashcards.cards
    cards = list(coll.find())
    for tag in tags:
        cards = [card for card in cards if len(
            [_tag for _tag in card["tags"] if match(tag, _tag) is not None]) > 0]
    return cards
