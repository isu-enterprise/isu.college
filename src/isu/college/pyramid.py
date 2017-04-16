
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

GSM = getGlobalSiteManager()


class WPListView(views.DefaultView):
    title = "Test"

    def __init__(self, location):
        self.location = os.path.abspath(location)
        self.files = glob(os.path.join(location + "/*.xls"))
        self.items = [os.path.split(fn)[-1] for fn in self.files]
        pprint(self.items)


wplistview = WPListView(resource_filename(
    'isu.college', "../../../data/study-plans/plans/"))

GSM.registerUtility(wplistview, name="study-plans")


@view_config(route_name="plan-list", renderer="isu.college:templates/splist.pt")
def work_plans(request):
    view = getUtility(IView, name="study-plans")
    return {
        "view": view,
        "context": "AAAAAAAAAA",
        "request": request,
        "response": request.response,
        "default": True,
    }


@view_config(route_name="plan", renderer="isu.college:templates/plan.pt")
def work_plan(request):
    plan_name = request.multidict["name"]
    print(plan_name)
    view = getUtility(IView, name="study-plans")
    view = view[name]
    return {
        "view": view,

    }


@adapter(IConfigurationEvent)
def configurator(config):
    config.add_route("plan", "/plans/${name}.html")
    config.add_route("plan-list", "/plans/")
    config.add_static_view(name='/lcss', path='isu.college:templates/lcss')
    config.scan()


GSM.registerHandler(configurator)
