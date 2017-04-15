from zope.interface import Interface
import zope.schema
from isu.onece.interfaces import IVocabularyItem, IVocabularyItemBase
from isu.onece.interfaces import IHierarchyBase
from isu.onece.org.interfaces import IEmployee
from isu.onece.org.interfaces import IOrganization, ISpecification
from isu.onece.org.interfaces import IEmployee
from zope.i18nmessageid import MessageFactory
import isu.college.enums as enums
# http://docs.plone.org/external/plone.app.dexterity/docs/advanced/vocabularies.html
# See more interesting at
# https://pypi.python.org/pypi/z3c.relationfield
#

_ = MessageFactory("isu.college")


# FIXME: Add default values for the fields.

class ICollege(IOrganization):
    pass


class IFaculty(IOrganization):
    pass


class IProfessor(IEmployee):
    """The faculty stuff unit, e.g.,
    human teacher. ;-)
    """


class IVocabularyItemSID(IVocabularyItem):
    id = zope.schema.TextLine(
        title=_("Code"),
        description=_(
            "The code identifying the catalog "
            "item represented as a string."),
        required=True,
        readonly=False
    )


class IProfession(IVocabularyItemSID, IHierarchyBase):
    """Teaching profession
    """


class IActivityType(IVocabularyItem):
    """Type of activity catalog.
    """


class IEducationalStandard(IVocabularyItemBase):
    """Reference to a educational standard.
    """
    # We suppose, that the view will seek the parents of
    # the profession hierarchy until a condition met.
    profession = zope.schema.Object(
        title=_("Teaching profession"),
        description=_("Reference to a teaching profession hierarchy."),
        schema=IProfession,
        # vocabulary="interface:IProfession",
        required=True
    )

    degree = zope.schema.Choice(
        title=_("Degree"),
        description=_("The degree to be obtained after education."),
        vocabulary=enums.Degree.vocabulary,
        required=True
    )


class ICurriculum(IVocabularyItemBase):
    """The curriculum supposed to be referenced from
    an IOrganization subdivision.
    """
    standard = zope.schema.Object(
        title=_("Educational standard"),
        description=_("Reference to an educational standard."),
        schema=IEducationalStandard,
        required=True
    )

    academicity = zope.schema.Choice(
        title=_("Academic relevance"),
        description=_(
            "The relevance of the degree to education or scholarship.."),
        vocabulary=enums.AcademicRelevance.vocabulary,
        required=True
    )

    mural = zope.schema.Choice(
        title=_("Mural type"),
        description=_("The mural form of the study process organization."),
        vocabulary=enums.Mural.vocabulary,
        required=True
    )

    training_period = zope.schema.Float(
        title=_("Training period"),
        description=_("The period of training in years"),
        required=True
    )

    start_year = zope.schema.Int(
        title=_("Start year"),
        description=_("The year the curriculum starts at"),
        required=True
    )

    activity_type = zope.schema.List(
        title=_("Type of activity"),
        description=_("List of various activity types"
                      "the curriculum educating to."),
        # FIXME: Constrain the possible object types.
        value_type=zope.schema.Choice(
            vocabulary='activity_type'
        )
    )
    # FIXME: Organization data and


class IEducationalSpecification(ISpecification):
    """A specification variation referring to
    a ICurriculum provider.
    """

    curriculum = zope.schema.Object(
        title=_("Curriculum"),
        description=_("The Curriculum the working program belongs to."),
        schema=ICurriculum,
        required=True
    )

    author = zope.schema.Object(
        title=_("Author"),
        description=_("The author of the specification"),
        schema=IProfessor,
    )


class IWorkingProgram(IEducationalSpecification):
    """The working program of discipline
    """


class IAcademicPlan(Interface):
    """Marker interface IAcaddemicPlan
    defines components denoting academic
    plans.
    """
