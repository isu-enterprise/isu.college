# Example package with a console entry point
from __future__ import print_function
__import__('pkg_resources').declare_namespace(__name__)


def includeme(global_config, **settings):
    from .pyramid import configurator
    configurator(global_config, **settings)
