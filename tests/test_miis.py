from nose.tools import raises
from isu.college.miis import Plan
from pkg_resources import resource_filename
import os.path
import glob
from pprint import pprint

DATADIR = os.path.abspath(
    os.path.join(
        resource_filename(
            'isu.college',
            "../../../"),
        "data/study-plans/plans/")
)

# TMPL = "*.pl*.xml.xls"
TMPL = "*.xls"

template = DATADIR + "/" + TMPL

# print(template)

ALLIN = glob.glob(template)

# print(DATADIR)
# print(len(ALLIN))
# pprint(ALLIN)


class TestBasic(object):

    def test_datadir(self):
        assert os.path.isdir(DATADIR)

    def test_allin_not_empty(self):
        assert len(ALLIN) > 0


class TestLoad(object):
    def setUp(self):
        FN = ALLIN[0]
        print(FN)
        self.plan = Plan(FN)

    def test_init(self):
        assert self.plan.program.direction.code
        assert self.plan.program.direction
        assert self.plan.program.profile
