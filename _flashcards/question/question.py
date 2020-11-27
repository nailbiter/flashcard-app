import logging
from datetime import date, datetime
import json


class Question():
    def __init__(self, card, deck, is_front_to_back, back_index):
        self._card = card
        self._deck = deck
        self._is_front_to_back = is_front_to_back
        self._back_index = back_index
        self._score = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def get_question_text(self):
        pass

    def _get_jinja_env(self):
        return {
            "card": self._card,
            "deck": self._deck,
            "is_front_to_back": self._is_front_to_back,
            "back_index": self._back_index,
            "score": self._score
        }

    def grade(self, answer):
        """
        :return (grade,msg): where grade from 0.0 to 1.0 or None if was not accepted; msg is optional message
        """
        self._given_answer = answer
        self._answer_time = datetime.now()
        return 0.0, None

    def to_json(self):
        assert self._score is not None
        res = {k: v for k, v in self._get_jinja_env().items(
        ) if k in ["is_front_to_back", "back_index", "score"]}
        res["card"] = str(self._card["_id"])
        res["given_answer"] = self._given_answer
        res["answer_time"] = self._answer_time.isoformat()
        res["TAG"] = self.__class__.TAG
        return json.dumps(res)

    def get_answer_options(self):
        return None

    def get_regrade_text(self):
        return None

    def regrade(self, answer):
        raise NotImplementedError
