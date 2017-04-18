from pyramid.paster import get_app, setup_logging
import sys
import os
from pprint import pprint, pformat
ini_path = '/home/eugeneai/Development/codes/isu-enterprise/college/isu.college/development.ini'
setup_logging(ini_path)
#raise RuntimeError(pformat(sys.path))
print("Reload...")
application = get_app(ini_path, 'main')
