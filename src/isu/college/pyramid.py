
from isu.webapp.interfaces import IConfigurationEvent

from pyramid.view import view_config
from zope.component import getGlobalSiteManager, adapter, getUtility
from isu.webapp import views
from glob import glob
from pprint import pprint
from pkg_resources import resource_filename
from icc.mvw.interfaces import IView, IViewRegistry
import os
import os.path
from .miis import Plan

GSM = getGlobalSiteManager()

DATADIR = os.path.abspath(
    os.path.join(
        resource_filename(
            'isu.college',
            "../../../"),
        "data/study-plans/plans/")
)


class View(views.DefaultView):
    auth_user = None


class StudyPlanVew(View):
    title = "Study Plan"

    def __init__(self, obj=None, filename=None):
        if self.obj is not None:
            self.plan = obj
        elif filename is not None:
            filename = os.path.join(DATADIR, filename)
            self.plan = Plan(filename)
        else:
            raise RuntimeError("either object or filename must be supplied")


class SPListView(View):
    title = "Test"

    def __init__(self, location):
        self.location = os.path.abspath(location)
        template = os.path.join(location + "/*.xls")
        self.files = glob(template)
        self.items = set([os.path.split(fn)[-1] for fn in self.files])
        self.plans = {}
        print("Location: {}".format(location))
        print("List of plans found.")
        pprint(self.items)

    def __getitem__(self, name):
        if name not in self.plans:

            print("Loading plan:{}".format(name))
            self.plans[name] = Plan(name)

        return self.plans[name]


splistview = SPListView(DATADIR)

GSM.registerUtility(splistview, name="study-plans")


@view_config(route_name="plan-list", renderer="isu.college:templates/splist.pt")
def work_plans(request):
    view = getUtility(IView, name="study-plans")
    return {
        "view": view,
    }


@view_config(route_name="plan", renderer="isu.college:templates/plan.pt")
def work_plan(request):
    plan_name = request.matchdict["name"]
    print(plan_name)
    view = getUtility(IView, name="study-plans")
    view = view[plan_name]
    return {
        "view": view,
    }


@adapter(IConfigurationEvent)
def configurator(config):
    config.add_route("plan", "/plans/{name}.html")
    config.add_route("plan-list", "/plans/")
    config.add_static_view(name='/lcss', path='isu.college:templates/lcss')
    config.scan()


GSM.registerHandler(configurator)
