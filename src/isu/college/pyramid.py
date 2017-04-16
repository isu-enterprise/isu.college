
from isu.webapp.interfaces import IConfigurationEvent

from pyramid.view import view_config
from zope.component import getGlobalSiteManager, adapter
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


@view_config(route_name="work-programs", renderer="isu.webapp:templates/index.pt")
def work_programs(request):
    view = getUtility(IView, name="study-plans")
    return {
        "view": view,
        "context": "AAAAAAAAAA",
        "request": request,
        "response": request.response,
        "default": True,
    }


@adapter(IConfigurationEvent)
def configurator(config):
    config.add_route("work-programs", "/wp/")
    config.scan()


GSM.registerHandler(configurator)
