from zope.interface import implementer
from icc.mvw.interfaces import IView
from collections import namedtuple
from appy.pod.renderer import Renderer
from pkg_resources import resource_filename

Stub = namedtuple('Stub', ["id", "name"])


@implementer(IView)
class FOSSpecificationView(object):

    def __init__(self, context):
        self.context = context
        self._profession = Stub(
            id="09.02.22", name="Информатика и вычислительная техника")

    @property
    def profession(self):
        return self.standard.profession

    @property
    def standard(self):
        return self.curriculum.standard

    @property
    def curriculum(self):
        return self.context.curriculum

    def __call__(self):
        return {'view': self, 'context': self.context}


def study_work_program(view, filename):
    infilename = resource_filename(
        'isu.college.app', 'templates/StudyWorkProgram.odt')

    Renderer(infilename, view(), filename)
