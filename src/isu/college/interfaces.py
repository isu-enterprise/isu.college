from zope.interface import Interface
import zope.schema
from isu.onece.interfaces import ICatalogItem
from isu.onece.org.interfaces import IEmployee, IDepartment
from isu.onece.org.interfaces import IOrganization, ISpecification


class ICollege(IOrganization):
    pass


class IFaculty(IOrganization):
    pass


class ISpeciality(ICatalogItem):
    pass


class IBachoirProgram(ICatalogItem):
    pass


class IWorkProgram(ISpecification):
    id = zope.schema.TextLine(
        title=_(""),

    )
