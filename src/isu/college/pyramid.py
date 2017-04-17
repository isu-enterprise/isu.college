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
from .interfaces import IAcademicPlan
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
        print(self.plan)
        return self.plan.program.direction


GSM.registerAdapter(StudyPlanVew)


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

    def getplan(self, name, course=None, form=None):
        if name not in self.plans:

            print("Loading plan:{}".format(name))
            fullpath = os.path.join(DATADIR, name)
            self.plans[name] = IView(Plan(fullpath))

        plan = self.plans[name]
        plan._filter = {
            "format": form,
            "course": course
        }
        return plan


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
    md = request.matchdict
    plan_name = md["name"]  # + ".xls"
    print(plan_name)
    view = getUtility(IView, name="study-plans")

    kwargs = {
        "course": md.get("course", None),
        "form": md.get("format", None)
    }

    view = view.getplan(plan_name, **kwargs)
    return {
        "view": view,
        "plan": view.plan
    }


@adapter(IConfigurationEvent)
def configurator(config):
    config.add_route("plan", "/plan/{name}.html")
    config.add_route("plan-list", "/plan/")
    config.add_static_view(name='/lcss', path='isu.college:templates/lcss')
    config.add_subscriber('isu.college.subscribers.add_base_template',
                          'pyramid.events.BeforeRender')
    config.scan()


GSM.registerHandler(configurator)
