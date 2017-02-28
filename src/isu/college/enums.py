import enum
from zope.schema.interfaces import IBaseVocabulary
from zope.interface import directlyProvides


class Mural(enum.Enum):
    Extramural = 0
    Extra = 0
    Intramural = 1
    Intra = 1


directlyProvides(Mural, IBaseVocabulary)


class Degree(enum.Enum):
    NoDegree = 0
    Bacheloir = 5
    Master = 6
    Magister = 7
    PhD = 8
    MD = 9
    Professor = 10


directlyProvides(Degree, IBaseVocabulary)


class AcademicRelevance(enum.Enum):
    """
    Программы прикладного бакалавриата рассчитаны на то,
    что выпускник получит больше практических навыков,
    пройдет длительную стажировку и по окончании вуза
    сможет "встать к станку".

    Академический бакалавриат дает больше теоретических
    знаний, и его выпускники более ориентированы на
    продолжение обучения в магистратуре.
    """
    Academс = 1
    Applied = 2


directlyProvides(AcademicRelevance, IBaseVocabulary)
