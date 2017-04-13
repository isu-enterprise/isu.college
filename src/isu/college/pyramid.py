
from isu.webapp.interfaces import IConfigurationEvent

from pyramid.view import view_config
from zope.component import getGlobalSiteManager, adapter

GSM = getGlobalSiteManager()


@view_config(route_name="work-programs", renderer="json")
def programs(request):
    return {"ok": True}


@adapter(IConfigurationEvent)
def configurator(config):
    #config.add_view(programs, route_name="work-programs", renderer="json")
    config.add_route("work-programs", "/work-programs/")
    config.scan()


GSM.registerHandler(configurator)
