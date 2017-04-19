from nose.plugins.skip import SkipTest
from nose.tools import assert_raises
from isu.college.app.fos import report
import pkg_resources
import os.path

OUTDIR = pkg_resources.resource_filename(
    "isu.college", "../../../tests/output")
INDIR = pkg_resources.resource_filename(
    "isu.college", "../../../tests/input")
OUTDIR = os.path.abspath(OUTDIR)
INDIR = os.path.abspath(INDIR)


@SkipTest
class TestImport:

    def test_import(self):
        pass

    def test_print_SWP(self):
        view = report.FOSSpecificationView(None)
        filename = "result.odt"
        filename = os.path.join(OUTDIR, filename)
        #report.study_work_program(view, filename)
