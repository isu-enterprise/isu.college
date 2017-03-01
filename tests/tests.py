from nose.plugins.skip import SkipTest
from nose.tools import assert_raises
from isu.college.interfaces import IProfessor
from isu.college import enums
from zope.schema.interfaces import IBaseVocabulary
from zope.schema.interfaces import ITokenizedTerm


class TestBasic:

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_interface(self):
        assert IProfessor


class TestEnums:

    def setUp(self):
        self.e = enums.Degree

    def test_degree(self):
        e = self.e
        assert IBaseVocabulary.providedBy(self.e)
        for a in self.e:
            ITokenizedTerm.providedBy(a)
            break
        else:
            assert False

        assert 0 in e
        assert -1 not in e
        assert e.getTermByToken("Master").value == 6
        assert e.getTermByToken("Master").value == e.context.Master
        assert e.getTerm(e.context.Master).value == e.context.Master
        assert e[e.context.Master].value == e.context.Master
        assert e[6].value == e.context.Master

    def test_enum_len(self):
        assert len(self.e) == 7

    def test_iterator(self):
        for term in self.e:
            assert term
