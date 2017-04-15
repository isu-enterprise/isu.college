from zope.component import adapter, getGlobalSiteManager
from isu.college.interfaces import IAcademicPlan
from isu.college.components import AcademicPlan
import xlrd
from isu.college import enums
import re

"""
This is a simple interpreter of page processor
that helps to find values among excel sheet

FIXME: Write good documentation.!!!

Structure has a form:
  {"<sheet name>":{
    <definitions>
  }}

where <definitions> are dicts of a form:
  {
     "<variable name>":(<commands>)
  }

<commands> ::= ( <start definition> [, <move or check>] [, proc func(x)])
<start definitions> ::= <cell addres, eg. A0> | <regexp>
<move or check> :: (dx,dy)* | "+" | (<rgexp>, <move>)
"+" as in regexps, one or many steps of the prev movement.
Move or check repeats till non-empty ...
  I.e. containing numbers or characters, nor spaces, /'s, _'s, etc.
... value found or
table border exit. In the last case the search failed.
"""

# Movement commands
L, R, D, U = (-1, 0), (1, 0), (0, 1), (0, -1)


class Plan(AcademicPlan):
    """Represents MIIS.ru Plan XLS export files as
    IAcademicPlan component.
    """

    def __init__(self, URL):
        self.URL = URL
        self.book = None
        self.load()

    def load(self):
        """Loads spreadsheet on demand
        or not.
        """
        if self.is_loaded():
            return

        self.book = xlrd.open_workbook(self.URL)
        self._run_recognition()
        self.debug_print()

    def is_loaded(self):
        return self.book is not None

    def degree_proc(self, x):
        return x.replace("подготовки ")

    def debug_print(self):
        book = self.book
        print("The number of worksheets is {0}".format(book.nsheets))
        print("Worksheet name(s): {0}".format(book.sheet_names()))
        sh = book.sheet_by_index(0)
        print("{0} {1} {2}".format(sh.name, sh.nrows, sh.ncols))
        print("Cell D30 is {0}".format(sh.cell_value(rowx=29, colx=3)))
        for rx in range(sh.nrows):
            print(sh.row(rx))

    def _run_recognition(self):
        SCRIPTS = {
            "Титул": {
                "ministry": ("C8"),
                "institution": ("A10"),
                "managers.rector": ("^Ректор$", "R*", self.slash_clean_proc),
                "program.degree": ("^УЧЕБНЫЙ ПЛАН;", "D", self.degree_proc),
                "program.direction": ("^направление ", self.direction_proc),
                "program.profile": ("^направление ", "D", self.profile_proc),
                "start_year": ("^Год начала подготовки$", "R"),
                "edu_standard.code": ("^Образовательный стандарт$", "R"),
                "edu_standard.title": ("^Образовательный стандарт$", "RD"),
                "managers.EW_prorector": ("^Проректор по учебной работе$",
                                          "R*", self.slash_clean_proc),
                "managers.UMU_head": ("^Начальник УМУ$", "R*",
                                      self.slash_clean_proc),
                "managers.director": ("^Директор$", "R*", self.slash_clean_proc),
                "approval.organization": ("^План одобрен", self.appov_plan_proc),
                "approval.organization": ("^План одобрен",
                                          "D", self.proto_number_proc),
                "chair.title": ("^Кафедра:$", "R"),
                "chair.faculty": ("^Факультет:$", "R"),
                "profession.degree": ("^Квалификация:", self.colon_split_proc),
                "profession.program": ("^Программа подготовки:", self.colon_split_proc),
                "profession.mural": ("^Форма обучения:", self.colon_split_proc),
                "program.duration": ("^Срок обучения:", self.g_removal_proc),
                "program.laboriousness": ("^Трудоемкость ОПОП:", self.colon_split_proc),
                "profession.activities": ("^Виды деятельности$", self.activities_proc),
            }
        }

    SLRE = re.compile("[\\/]?(.*)[\\/]?")  # Not used

    def slash_clean_proc(self, s):
        """/XXXX/ -> XXX """
        return s.replace("/", "").replace("\\", "")

    DRE = re.compile("((\d\.)+\d).\s*(.*)")

    def direction_proc(self, s):
        s = s.replace("направление ", "").strip()
        m = DRE.match(s)
        assert m is not None, "cannot match"
        return {
            "code": m.group(1),
            "title": m.group(3)
        }

    def profile_proc(self, s):
        s = s.split('"')[2]
        return s

    def appov_plan_proc(self, s):
        return s.replace("План одобрен ", "")

    def proto_number_proc(self, s):
        return s.replace("Протокол ", "")

    def colon_split_proc(self, s):
        return s.split(":")[2].strip()

    def g_removal_proc(self, s):
        return s.replace("г", "")

    def activities_proc(self, s):
        l = s.split("\n")
        l = [a.strip("- ", "") for a in l]
        return l
