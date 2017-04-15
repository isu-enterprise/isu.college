from zope.component import adapter
from isu.college.interfaces import IAcademicPlan


class AcademicPlan(object):
    """The AcademicPlan represents a plan of
    study.
    """

    def __init__(self, args):
        super(AcademicPlan, self).__init__()
        self.args = args
