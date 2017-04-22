from .interfaces import IAcademicPlan, IAcademicCourse
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


@implementer(IAcademicCourse)
class AcademicCourse(object):
    """Represents an academic course
    """

    def __init__(self, name=None, title=None):
        self.name = name
        self.title = title
