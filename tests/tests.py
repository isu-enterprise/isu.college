from nose.plugins.skip import SkipTest
from nose.tools import assert_raises
from isu.college.interfaces import IProfessor


class TestBasic:

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_interface(self):
        assert IProfessor
