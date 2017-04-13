
from isu.webapp.interfaces import IConfigurationEvent

from pyramid.view import view_config
from zope.component import getGlobalSiteManager, adapter

GSM = getGlobalSiteManager()


@adapter(IConfigurationEvent)
def configurator(configurator):
    print("OK!!!!!")


GSM.registerHandler(configurator)
