import enum
from zope.schema.interfaces import IBaseVocabulary
from zope.interface import directlyProvides
from isu.enterprise.enums import vocabulary


@vocabulary('mural')
@enum.unique
class Mural(enum.IntEnum):
    Extramural = 0
    Intramural = 1


@vocabulary('degree')
@enum.unique
class Degree(enum.IntEnum):
    NoDegree = 0
    Bacheloir = 5   # Бакалавр
    Specialist = 6  # Специалист
    Master = 7      # Магистр
    PhD = 8
    MD = 9
    Professor = 10


@vocabulary('academicity')
@enum.unique
class AcademicRelevance(enum.IntEnum):
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
