from secretary import Renderer
from .test_fos_apps import OUTDIR, INDIR
import os.path
from isu.college import enums


class TestSecretary:

    def setUp(self):
        self.engine = Renderer()
        self.TEMPLATE = os.path.join(INDIR, "StudyWorkProgram.odt")

    def test_render(self):
        outfile = os.path.join(OUTDIR, "result-def-render.odt")
        o = open(outfile, "wb")
        for t in enums.Degree.vocabulary:
            print(t.token, int(t.value))
        result = self.engine.render(
            self.TEMPLATE, code="09.11.12", name="Программа Сети и компьютеры.", degrees=enums.Degree.vocabulary)
        o.write(result)
        o.close()
