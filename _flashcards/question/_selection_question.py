from _flashcards.question.question import Question
import logging
from random import sample, shuffle
from jinja2 import Template
import os


class _SelectionQuestion(Question):
    TAG = "selection"
    _NUMBER_OF_ANSWERS = int(os.environ.get("SELECTION_QUESTION_ANSWERNUM", 3))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert len(self._deck) > _SelectionQuestion._NUMBER_OF_ANSWERS > 1

        self._logger.info(f"card: {self._card}")
        self._answers = []
        other_cards = sample([c for c in self._deck if c["_id"]
                              != self._card["_id"]], self._NUMBER_OF_ANSWERS-1)
        _aux = ",".join([b for i, b in enumerate(
            self._card["back"]) if i != self._back_index])
        if len(_aux) > 0:
            _aux = f" ({_aux})"
        if self._is_front_to_back:
            self._question = self._card["front"]+_aux
            self._answers.append(self._card["back"][self._back_index])
            for card in other_cards:
                _back_index = min(len(card["back"])-1, self._back_index)
                self._answers.append(card["back"][_back_index])
        else:
            self._question = self._card["back"][self._back_index]+_aux
            self._answers = [self._card["front"], *
                             [card["front"] for card in other_cards]]

        enumerated_answers = list(enumerate(self._answers))
        shuffle(enumerated_answers)
        self._correct_answer = next(
            answer for i, (old_i, answer) in enumerate(enumerated_answers) if old_i == 0)
        self._answers = [a for i, a in enumerated_answers]

    def _get_jinja_env(self):
        return {
            **super()._get_jinja_env(),
            "answers": self._answers,
            "question": self._question,
        }

    def grade(self, answer):
        super().grade(answer)
        try:
            ai = int(answer)
        except ValueError:
            return None, "not a number"
        if ai <= 0 or ai > _SelectionQuestion._NUMBER_OF_ANSWERS:
            return None, "answer should be >=0"
        else:
            self._logger.info(f"answer: {ai}")
            self._logger.info(
                f"correct_answer: {self._correct_answer}")
            is_correct = self._answers[ai-1] == self._correct_answer
            self._score = 1.0 if is_correct else 0.0
            return self._score, None if is_correct else self._correct_answer

    def get_question_text(self):
        env = self._get_jinja_env()
        return Template("""
        select the correct answer for "{{question}}":
        {%for i in range(answers|length)-%}
        {{i+1}}. {{answers[i]}}
        {%endfor-%}
        """).render(**env)

    def get_answer_options(self):
        return range(1, _SelectionQuestion._NUMBER_OF_ANSWERS+1)
