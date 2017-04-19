from nose.plugins.skip import SkipTest
from nose.tools import assert_raises
from isu.college.interfaces import IProfessor
from isu.college import enums
from zope.schema.interfaces import IBaseVocabulary
from zope.schema.interfaces import ITokenizedTerm
from zope.schema.vocabulary import getVocabularyRegistry


@SkipTest
class TestBasic:

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_interface(self):
        assert IProfessor


@SkipTest
class TestEnums:

    def setUp(self):
        registry = getVocabularyRegistry()
        self.e = registry.get(None, 'degree')

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
        assert e.getTermByToken("Specialist").value == 6
        assert e.getTermByToken("Specialist").value == e.enum.Specialist
        assert e.getTerm(e.enum.Specialist).value == e.enum.Specialist
        assert e[e.enum.Specialist].value == e.enum.Specialist
        assert e[6].value == e.enum.Specialist

    def test_enum_len(self):
        assert len(self.e) == 7

    def test_iterator(self):
        for term in self.e:
            assert term

# Do the same checking vocabulary availability.


@SkipTest
class TestEnums2(TestEnums):

    def setUp(self):
        self.e = enums.Degree.vocabulary
