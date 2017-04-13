
from isu.webapp.interfaces import IConfigurationEvent

from pyramid.view import view_config
from zope.component import getGlobalSiteManager, adapter
from isu.webapp import views

GSM = getGlobalSiteManager()


class View(views.DefaultView):
    title = "Test"
    pass


@view_config(route_name="work-programs", renderer="isu.webapp:templates/index.pt")
#@view_config(route_name="work-programs", renderer="json")
def work_programs(request):
    return {
        "view": View(),
        "request": request,
        "response": request.response,
        "default": True,
    }


@adapter(IConfigurationEvent)
def configurator(config):
    config.add_route("work-programs", "/work-programs/")
    config.scan()


GSM.registerHandler(configurator)
