from nose.tools import raises
from isu.college.miis import Plan
from pkg_resources import resource_filename
import os.path

DATADIR = os.path.abspath(
    os.path.join(
        resource_filename('isu.college', "data/study-plans/plans"), "../../../")
)


class TestLoad(object):
    def setUp(self):
        self.plan = ()
