from zope.component import adapter, getGlobalSiteManager
from isu.college.interfaces import IAcademicPlan
from isu.college.components import AcademicPlan
import xlrd
from isu.college import enums
import re
import marisa_trie
import pymorphy2
from pprint import pprint

morph = pymorphy2.MorphAnalyzer()

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


class NormalizationError(Exception):
    pass


def normal(word, *tags):
    tags = set(tags)
    for p in morph.parse(word):
        if tags in p.tag:
            return p.normal_form
    raise NormalizationError(
        "cannot normaize '{}' within {}".format(word, tags))


def move(row, col, direction):
    dx, dy = MOVES[direction]
    yield row + dy, col + dx


class Object(object):
    def __str__(self):
        s = "{}<{}>:\n".format(self.__class__.__name__, hex(id(self)))
        for k in dir(self):
            if not k.startswith("_"):
                val = getattr(self, k)
                s += "{}={}\n".format(k, val)
        s += "\n"
        return s


class String(str, Object):
    pass


class Plan(AcademicPlan):
    """Represents MIIS.ru Plan XLS export files as
    IAcademicPlan component.
    """

    def __init__(self, URL):
        self.URL = URL
        self.book = None
        self.attrs = {}
        self.load()

    def __str__(self):
        s = "{}<{}>:\n".format(self.__class__.__name__, hex(id(self)))
        for k in self.attrs.keys():
            if not k.startswith("_"):
                val = self.attrs[k]
                s += "{}={}\n".format(k, repr(val))
        s += "\n"
        return s

    def load(self):
        """Loads spreadsheet on demand
        or not.
        """
        if self.is_loaded():
            return

        self.book = xlrd.open_workbook(self.URL)
        self._setup_rules()
        self._run_recognition()
        pprint(self.attrs)
        self._represent()
        # print(self.program.direction)
        # self.debug_print()

    def is_loaded(self):
        return self.book is not None

    VALSTRRE = re.compile("(\w+|\d+)")

    def check(self, cell):
        if cell is None:
            return False
        if hasattr(cell, "ctype"):
            if cell.ctype == 0:
                return False
        if self.VALSTRRE.search(cell.value) is None:
            return False
        return True

    def path(self, cell, sheet, row, col,
             direction,
             skip_first=True,
             max_steps=-1,
             steps=-1
             ):

        dx, dy = direction  # MOVES[direction]
        nrows, ncols = sheet.nrows, sheet.ncols
        if not skip_first:
            if self.check(cell):
                yield cell, sheet, row, col
        while True:
            if steps == 0 or max_steps == 0:
                return

            row, col = row + dy, col + dx
            max_steps -= 1
            steps -= 1

            if row < 0 or col < 0 or row >= nrows or col >= ncols:
                return

            cell = sheet.cell(rowx=row, colx=col)
            if self.check(cell):
                if steps < 0 or steps == 0:
                    yield cell.value, sheet, row, col

    def degree_proc(self, val, sheet, row, col):
        sb = "подготовки"
        for val, sheet, row, col in self.path(val, sheet, row, col, D):
            val = val.strip()
            if val.startswith(sb):
                yield (normal(val.replace(sb, ""), "NOUN"), sheet, row, col)
                break

    def debug_print(self):
        book = self.book
        print("The number of worksheets is {0}".format(book.nsheets))
        print("Worksheet name(s): {0}".format(book.sheet_names()))
        sh = book.sheet_by_index(0)
        print("{0} {1} {2}".format(sh.name, sh.nrows, sh.ncols))
        print("Cell D30 is {0}".format(sh.cell_value(rowx=29, colx=3)))
        for rx in range(sh.nrows):
            print(sh.row(rx))

    def _setup_rules(self):
        self.RULES = {
            "Титул": {
                "ministry": ((7, 2), self.identity),
                "institution": ((9, 0), self.identity),
                "managers.rector": ("Ректор", self.slash_clean_proc),
                "program.degree": ("УЧЕБНЫЙ ПЛАН", self.degree_proc),
                "program.direction": ("^[нН]аправление", self.direction_proc),
                "program.profile": ("^[нН]аправление ", self.profile_proc),
                "program.start_year": ("^[Гг]од начала подготовки$", self.right_proc),
                "edu_standard": ("^[Оо]бразовательный стандарт$", self.edu_standard_proc),
                "managers.EW_prorector": ("^[Пп]роректор.*учеб.*работе$", self.slash_clean_proc),
                "managers.UMU_head": ("^[Нн]ачальник УМУ$", self.slash_clean_proc),
                "managers.director": ("^[Дд]иректор$", self.slash_clean_proc),
                "approval": ("^[Пп]лан одобрен", self.appov_plan_proc),
                "chair.title": ("^Кафедра:$", self.right_proc),
                "chair.faculty": ("^Факультет:$", self.right_proc),
                "profession.degree": ("^Квалификация:", self.colon_split_proc),
                "profession.program": ("^Программа подготовки:", self.colon_split_proc),
                "profession.mural": ("^Форма обучения:", self.colon_split_proc),
                "program.duration": ("^Срок обучения:", self.g_removal_proc),
                "program.laboriousness": ("^Трудоемкость ОПОП:", self.colon_split_proc),
                "profession.activities": ("^Виды деят", self.activities_proc),
            }
        }

    def _represent(self, d=None, o=None):
        if d is None:
            d = self.attrs
            o = self
        assert "_value" not in d or o != self, "wrong structure"
        for k, v in d.items():
            if k == "_value":
                continue

            if isinstance(v, dict):
                if "_value" in v:
                    n = String(v["_value"])
                else:
                    n = Object()
                self._represent(v, n)
                v = n
            setattr(o, k, v)

    def _run_recognition(self):

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

        for page, matchs in self.RULES.items():
            sheet = self.book.sheet_by_name(page)

            for var, prog in matchs.items():
                templ, body = prog
                # body = getattr(self, body)

                for cell, row, col in find_match(sheet, templ):
                    assert cell is not None and cell.ctype != 0
                    for _ in body(cell.value, sheet, row, col):
                        assert len(_) >= 4, "must yield (val, sheet, row, col)"
                        if _[0] is None:
                            continue
                        cell = _[0]
                        break
                    else:
                        continue
                    if cell is not None:
                        if hasattr(cell, "ctype"):
                            if cell.ctype == 0:
                                continue
                            self.assign(cell.value, name=var)
                        else:
                            self.assign(cell, name=var)
                        break

        print(self)

    def assign(self, value, name):
        assert value is not None
        if isinstance(value, dict):
            for k, v in value.items():
                nname = name.rstrip(".")
                if k == "_value":
                    self.assign(v, nname)
                else:
                    nname += "." + k
                    self.assign(v, nname)
        else:
            if isinstance(value, str):
                value = value.strip()
            path = name.split(".")
            attrs = self.attrs
            for name in path:
                attrs = attrs.setdefault(name, {})
            attrs.update({"_value": value})

    def identity(self, cell, *args):
        yield (cell,) + args

    SLRE = re.compile("[\\/]?(.*)[\\/]?")  # Not used

    def slash_clean_proc(self, val, sheet, row, col):
        """/XXXX/ -> XXX """
        for val, _, r, c in self.right_proc(val, sheet, row, col):
            yield val.replace("/", "").replace("\\", "").strip(), sheet, r, c
            break

    DRE = re.compile(".*(\s(\d+\.\d+\.\d+)\.?\s*(.*))")

    def direction_proc(self, val, sheet, row, col):
        val = val.strip()
        m = self.DRE.match(val)
        if m is None:
            return
        assert m is not None, "cannot match {} with {}".format(val, self.DRE)
        val = {
            "code": m.group(2),
            "title": m.group(3),
            "_value": m.group(1)
        }
        yield val, sheet, row, col

    def profile_proc(self, val, sheet, row, col):
        for val, sheet, row, col in self.path(val,
                                              sheet,
                                              row,
                                              col,
                                              direction=D, steps=1):
            val = val.replace("'", "\"").split('"')[1]
            yield val, sheet, row, col
            break

    def right_one_proc(self, val, sheet, row, col):
        for val, sheet, row, col in self.path(val,
                                              sheet,
                                              row,
                                              col,
                                              direction=R, steps=1):
            yield val, sheet, row, col
            break

    def right_proc(self, val, sheet, row, col, max_steps=-1, steps=-1):
        for val, sheet, row, col in self.path(val,
                                              sheet,
                                              row,
                                              col,
                                              direction=R,
                                              steps=steps,
                                              max_steps=max_steps
                                              ):
            yield val, sheet, row, col
            break

    def down_proc(self, val, sheet, row, col, max_steps=-1, steps=-1):
        for val, sheet, row, col in self.path(val,
                                              sheet,
                                              row,
                                              col,
                                              direction=D,
                                              steps=steps,
                                              max_steps=max_steps
                                              ):
            yield val, sheet, row, col
            break

    def down_one_proc(self, val, sheet, row, col, steps=1):
        for val, sheet, row, col in self.path(val,
                                              sheet,
                                              row,
                                              col,
                                              direction=D, steps=1):
            yield val, sheet, row, col
            break

    def edu_standard_proc(self, val, sheet, row, col):
        for code, _, r, c in self.right_proc(val, sheet, row, col):
            break
        else:
            return
        for date, _, r, c in self.down_one_proc(val, sheet, r, c, steps=1):
            break
        else:
            return

        yield {
            "code": code,
            "date": date
        }, sheet, r, c

    def appov_plan_proc(self, v, s, r, c):
        division = v.split("одобрен ")[1].strip()
        for v, s, r, c in self.down_one_proc(v, s, r, c):
            for v, s, r, c in self.right_proc(v, s, r, c):
                number, date = v.split(" от ")
                yield {
                    "division": division,
                    "signature.number": number,
                    "signature.date": date
                }, s, r, c
                return

    def proto_number_proc(self, s):
        return s

    def colon_split_proc(self, v, s, r, c):
        yield v.split(":")[1].strip(), s, r, c

    def g_removal_proc(self, v, s, r, c):
        for v, s, r, c in self.colon_split_proc(v, s, r, c):
            yield v.replace("г", ""), s, r, c
            break

    WORDDASHRE = re.compile("(\w+\s?-?\s?\w+)")

    def activities_proc(self, v, s, r, c):
        for v, s, r, c in self.right_proc(v, s, r, c):
            l = self.WORDDASHRE.findall(v)
            l = [a.strip().replace(" ", "") for a in l]
            l = [a for a in l if a]
            yield l, s, r, c
            break
