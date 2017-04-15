from .interfaces import IAcademicPlan
from zope.interface import implementer
from collections import namedtuple


Vocab = namedtuple("Vocab", ["code", "title"])


@implementer(IAcademicPlan)
class AcademicPlan(object):
    """The AcademicPlan represents a plan of
    study.
    """

    def __init__(self):
        pass

    @property
    def profession(self):
        return Vocab("09.03.03", "Прикладная информатика")
