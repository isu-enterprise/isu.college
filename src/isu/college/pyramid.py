from isu.webapp.interfaces import IConfigurationEvent
from zope.component import adapter

from pyramid.view import view_config
from isu.webapp.views import View
from glob import glob
from pprint import pprint
from pkg_resources import resource_filename
from icc.mvw.interfaces import IView, IViewRegistry
import os
import os.path
from .interfaces import IAcademicPlan
from .miis import Plan

DATADIR = os.path.abspath(
    os.path.join(
        resource_filename(
            'isu.college',
            "../../../"),
        "data/study-plans/plans/")
)


@adapter(IAcademicPlan)
class StudyPlanVew(View):

    def __init__(self, obj=None, filename=None):
        if obj is not None:
            self.plan = obj
        elif filename is not None:
            filename = os.path.join(DATADIR, filename)
            self.plan = Plan(filename)
        else:
            raise RuntimeError("either object or filename must be supplied")

    @property
    def title(self):
        # print(self.plan)
        return self.plan.program.direction

    @property
    def loc(self):
        """Return list of competence filtered.
        """
        filter = self.filter
        if filter is not None:
            yield from self.plan.show_list(
                self.plan.compl,
                filterid=filter["course"],
                form="{title} ({code})"
            )
        else:
            yield from self.plan.competence_list


# GSM.registerAdapter(StudyPlanVew)


class SPListView(View):
    title = "Test"

    def __init__(self, location):
        # FIXME: Add standard arguments
        super(SPListView, self).__init__()
        self.location = os.path.abspath(location)
        template = os.path.join(location + "/*.xlsx")
        self.files = glob(template)
        self.items = set([os.path.split(fn)[-1] for fn in self.files])
        self.plan_views = {}
        #print("Location: {}".format(location))
        #print("List of plans found.")
        # pprint(self.items)

    def getplan(self, name):
        if name not in self.plan_views:

            print("Loading plan:{}".format(name))
            fullpath = os.path.join(DATADIR, name)
            plan_view = self.registry.getAdapter(
                Plan(fullpath), interface=IView)
            plan_view.filename = name
            plan_view.filepathname = fullpath
            self.plan_views[name] = plan_view

        plan_view = self.plan_views[name]
        return plan_view


splistview = SPListView(DATADIR)


@view_config(route_name="plan-list", renderer="isu.college:templates/splist.pt")
def work_plans(request):
    view = request.registry.getUtility(IView, name="study-plans")
    return {
        "view": view,
    }


@view_config(route_name="plan", renderer="isu.college:templates/plan.pt")
def work_plan(request):
    md = request.matchdict
    plan_name = md["name"]
    view = request.registry.getUtility(IView, name="study-plans")

    if plan_name.endswith(".xlsx"):
        view = view.getplan(plan_name)
        view.filter = None
    else:
        parts = plan_name.split(".xlsx")
        plan_name = parts[0] + ".xlsx"
        view = view.getplan(plan_name)

        course, form = (parts[1].split("-") + [None, None])[1:3]

        kwargs = {
            "course": course,
            "format": form
        }
        view.filter = kwargs

    return {
        "view": view,
        "plan": view.plan
    }


#@adapter(IConfigurationEvent)
def configurator(config):
    config.load_zcml("isu.college:configure.zcml")
    config.add_route("plan", "/plan/{name}.html")
    config.add_route("plan-list", "/plan/")
    config.add_static_view(name='/lcss', path='isu.college:templates/lcss')
    config.add_subscriber('isu.college.subscribers.add_base_template',
                          'pyramid.events.BeforeRender')
    config.scan()


def zcml(config):
    """Runs zcml configuration on the
    config object.
    FIXME: Get rid of this (zcml(..)) shame stauff. ;-)
    """
    # print("REG---------------")
    # print(list(config.registry.registeredSubscriptionAdapters()))
    config.add_subscriber(configurator, IConfigurationEvent)
