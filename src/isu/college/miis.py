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

# Movement commands (dx,dy)
L, R, D, U = (-1, 0), (1, 0), (0, 1), (0, -1)

MOVES = {
    "L": L,
    "R": R,
    "D": D,
    "U": U
}


class CellNotFoundError(Exception):
    pass


class Object(object):
    def __str__(self):
        s = "{}<{}>:\n".format(self.__class__.__name__, hex(id(self)))
        for k in dir(self):
            if not k.startswith("_"):
                val = getattr(self, k)
                s += "{}={}\n".format(k, val)
        s += "\n"
        return s


class Plan(AcademicPlan, Object):
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
        # self.debug_print()

    def is_loaded(self):
        return self.book is not None

    def degree_proc(self, x):
        return x.replace("подготовки ", "")

    def debug_print(self):
        book = self.book
        print("The number of worksheets is {0}".format(book.nsheets))
        print("Worksheet name(s): {0}".format(book.sheet_names()))
        sh = book.sheet_by_index(0)
        print("{0} {1} {2}".format(sh.name, sh.nrows, sh.ncols))
        print("Cell D30 is {0}".format(sh.cell_value(rowx=29, colx=3)))
        for rx in range(sh.nrows):
            print(sh.row(rx))

    VALSTRRE = re.compile("(\w+|\d+)")

    def _run_recognition(self):
        SCRIPTS = {
            "Титул": {
                #"ministry": ((7, 2),),
                #"institution": ((9, 0),),
                # "managers.rector": ("^Ректор$", "R+", self.slash_clean_proc),
                # "program.degree": ("^УЧЕБНЫЙ ПЛАН", "DD", self.degree_proc),
                #- "program.direction": ("^направление ", self.direction_proc),
                #- "program.profile": ("^направление ", "D", self.profile_proc),
                #- "start_year": ("^Год начала подготовки$", "R"),
                #-"edu_standard.code": ("^Образовательный стандарт$", "R"),
                #-"edu_standard.title": ("^Образовательный стандарт$", "RD"),
                #"managers.EW_prorector": ("^Проректор по учебной работе$",
                #                          "R+", self.slash_clean_proc),
                #"managers.UMU_head": ("^Начальник УМУ$", "R+",
                #                      self.slash_clean_proc),
                # "managers.director": ("^Директор$", "R+", self.slash_clean_proc),
                # "approval.organization": ("^План одобрен", self.appov_plan_proc),
                #-"approval.number": ("^План одобрен",
                #                    "DR", self.proto_number_proc),
                #-"chair.title": ("^Кафедра:$", "R"),
                #-"chair.faculty": ("^Факультет:$", "R"),
                # "profession.degree": ("^Квалификация:", self.colon_split_proc),
                # "profession.program": ("^Программа подготовки:", self.colon_split_proc),
                # "profession.mural": ("^Форма обучения:", self.colon_split_proc),
                # "program.duration": ("^Срок обучения:", self.g_removal_proc),
                # "program.laboriousness": ("^Трудоемкость ОПОП:", self.colon_split_proc),
                "profession.activities": ("^Виды деят", "R", self.activities_proc),
                #"profession.activities": ("^Виды деят", self.activities_proc),
            }
        }

        # ADDRRE = re.compile("\w+\d+")  # A0 C10

        def find_match(sheet, templ):
            if isinstance(templ, (tuple, list)):
                row, col = templ
                cell = sheet.cell(rowx=row, colx=col)
                if cell.ctype == 0:
                    cell = None
                yield cell, row, col
                return

            rege = re.compile(templ)
            for row in range(sheet.nrows):
                for col in range(sheet.ncols):
                    cell = sheet.cell(rowx=row, colx=col)
                    if cell.ctype != 0:
                        val = cell.value.strip()
                        # print(col, row, val, cell, cell.ctype)
                        m = rege.match(val)
                        if m is not None:
                            yield cell, row, col

        def process_body(sheet, cell, body, row, col):
            def mv(c, x, y):
                dx, dy = MOVES[c]
                return (x + dx, y + dy)

            def interp(row, col):
                col, row = mv(r, col, row)
                if row < 0 or col < 0 or \
                   row >= sheet.nrows or \
                   col > sheet.ncols:
                    raise CellNotFoundError("gone beyond the sheet")

                cell = sheet.cell(rowx=row, colx=col)
                if cell.ctype == 0:
                    return True, cell, row, col

                val = cell.value
                if self.VALSTRRE.search(val) is not None:
                    return False, cell, row, col
                return True, cell, row, col

            for i, cmd in enumerate(body):
                if isinstance(cmd, str):
                    pc = None
                    r = None
                    for c in cmd:
                        r = c
                        if c == "+":
                            r = pc
                            next_ = True
                            while next_:
                                next_, cell, row, col = interp(row, col)
                            pc = None

                        else:
                            _, cell, row, col = interp(row, col)
                            pc = c

                elif isinstance(cmd, type(self.g_removal_proc)):
                    if cell.ctype == 0:
                        return None
                    val = cmd(cell.value)
                    return val

            if cell is None or cell.ctype == 0:
                return None

            return cell.value

        def assign_val(o, val):
            if isinstance(val, dict):
                if not isinstance(o, Object):
                    n = Object()
                    if o is not None:
                        setattr(n, "value", o)
                    o = n

                for k, v in val.items():
                    setattr(o, k, v)
                return o
            return val

        for page, matchs in SCRIPTS.items():
            sheet = self.book.sheet_by_name(page)

            for var, prog in matchs.items():
                templ = prog[0]
                rest = prog[1:]
                cell = None

                for cell, row, col in find_match(sheet, templ):
                    cell = process_body(sheet, cell, rest, row, col)
                    if cell is None:
                        continue

                l = var.split(".")
                if hasattr(self, var):
                    oval = getattr(self, var)
                else:
                    oval = None
                if len(l) == 1:
                    setattr(self, var, assign_val(oval, cell))
                else:
                    field, subf = l
                    if hasattr(self, field):
                        o = getattr(self, field)
                        print("O:", o)
                        assert isinstance(o,
                                          Object), \
                            "field '{}' is not an " \
                            "Object instance!".format(field)
                    else:
                        o = Object()
                        setattr(self, field, o)
                    if hasattr(o, subf):
                        oval = getattr(o, subf)
                    else:
                        oval = None
                    setattr(o, subf, assign_val(oval, cell))
        print(self)

    SLRE = re.compile("[\\/]?(.*)[\\/]?")  # Not used

    def slash_clean_proc(self, s):
        """/XXXX/ -> XXX """
        return s.replace("/", "").replace("\\", "").strip()

    DRE = re.compile("((\d\.)+\d).\s*(.*)")

    def direction_proc(self, s):
        s = s.replace("направление ", "").strip()
        m = self.DRE.match(s)
        assert m is not None, "cannot match"
        return {
            "code": m.group(1),
            "title": m.group(3)
        }

    def profile_proc(self, s):
        s = s.split('"')[2]
        return s

    def appov_plan_proc(self, s):
        return s.replace("План одобрен ", "").strip()

    def proto_number_proc(self, s):
        return s

    def colon_split_proc(self, s):
        return s.split(":")[1].strip()

    def g_removal_proc(self, s):
        return self.colon_split_proc(s).replace("г", "")

    def activities_proc(self, s):
        return (s)
        l = s.split("\n")
        l = [a.strip("- ") for a in l]
        return l
