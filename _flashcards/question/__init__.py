from _flashcards.question._selection_question import _SelectionQuestion
from _flashcards.question._typein_question import _TypeinQuestion


_QUESTION_CLASSES = [_SelectionQuestion, _TypeinQuestion]


def get_question_types():
    return [cls.TAG for cls in _QUESTION_CLASSES]


def get_question(type_, *args, **kwargs):
    _d = {cls.TAG: cls for cls in _QUESTION_CLASSES}
    assert type_ in _d
    return _d[type_](*args, **kwargs)
