"""===============================================================================

        FILE: /Users/nailbiter/for/forpython/flashcard-app/_flashcards/question/_typein_question.py

       USAGE: (not intended to be directly executed)

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: ---
     CREATED: 2020-10-31T20:28:03.665896
    REVISION: ---

==============================================================================="""

from _flashcards.question.question import Question
from difflib import SequenceMatcher
from datetime import datetime


class _TypeinQuestion(Question):
    TAG = "typein"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aux = ",".join([b for i, b in enumerate(
            self._card["back"]) if i != self._back_index])
        if len(_aux) > 0:
            _aux = f" ({_aux})"
        if self._is_front_to_back:
            self._question = self._card["front"]+_aux
            self._answer = self._card["back"][self._back_index]
        else:
            self._question = self._card["back"][self._back_index]+_aux
            self._answer = self._card["front"]

    def get_question_text(self):
        return self._question

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
        if not answer:
            return None, "answer should be nonempty"
        self._given_answer = answer
        self._answer_time = datetime.now()
        sm = SequenceMatcher(lambda x:x in ", ",answer,self._answer)
        self._score = sm.ratio()
        return self._score, answer + ('==' if self._score==1.0 else '!=') + self._answer
    _GRADE_AS_TRUE_AFFIRM_CODE = "a4bc476591d4"
    def get_regrade_text(self):
        return f"""
        press   `{self.__class__._GRADE_AS_TRUE_AFFIRM_CODE}` to mark true, anything else to continue

        """.strip()
    def regrade(self,answer):
        if answer==self.__class__._GRADE_AS_TRUE_AFFIRM_CODE:
            self._given_answer = self.__class__._GRADE_AS_TRUE_AFFIRM_CODE
            self._answer_time = datetime.now()
            self._score = 1.0
            return self._score, "regraded as correct"
        else:
            return self._score, "leave as it was"
