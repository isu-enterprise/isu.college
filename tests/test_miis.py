from nose.tools import raises, nottest
from isu.college.miis import Plan
from pkg_resources import resource_filename
import os.path
import glob
from pprint import pprint
from nose.plugins.skip import SkipTest
import openpyxl
from isu.college.miis import Index

DATADIR = os.path.abspath(
    os.path.join(
        resource_filename(
            'isu.college',
            "../../../"),
        "data/study-plans/plans/")
)

# TMPL = "*.pl*.xml.xlsx"
TMPL = "*.xlsx"

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


#@SkipTest
class TestLoad(object):
    def setUp(self):
        i = 4
        FN = ALLIN[i]
        print(i, FN)
        self.plan = Plan(FN)

    #@nottest
    def test_init(self):
        assert self.plan.program.direction.code
        assert self.plan.program.direction
        assert self.plan.program.profile

    def test_plan_load(self):
        plan = self.plan
        plan.load_plan()
        pprint(dir(plan.colidx))
        assert plan.colidx.course[1].total.h


@SkipTest
class TestAllKnown:
    def setUp(self):
        self.files = ALLIN

    @nottest
    def test_allin(self):
        for i, f in enumerate(self.files):
            print("{}-th plan:{}".format(i, f))
            plan = Plan(f)
            self.check(plan)

    @nottest
    def check(self, p):
        assert p.program.direction.code
        assert p.program.direction
        assert p.program.profile
        assert p.profession


@SkipTest
class TestOpenPYXL(object):
    """Tests basics of openpyxl

    """

    def setUp(self):
        i = 4
        FN = ALLIN[i]
        print(i, FN)
        self.book = openpyxl.load_workbook(filename=FN)

    def test_select(self):
        b = self.book
        b['План']

    def test_index(self):
        i = Index(1)
        i.a = Index(20)
        i.a.b = Index(40)
        assert i.a == 20
