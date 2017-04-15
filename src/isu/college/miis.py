from zope.component import adapter, getGlobalSiteManager
from isu.college.interfaces import IAcademicPlan
from isu.college.components import AcademicPlan
import xlrd


class Plan(AcademicPlan):
    """Represents MIIS.ru Plan XLS export files as
    IAcademicPlan component.
    """

    def __init__(self, URL):
        self.URL = URL
