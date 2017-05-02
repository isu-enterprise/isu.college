from isu.webapp.interfaces import IConfigurationEvent
from zope.component import adapter
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.response import FileResponse

from pyramid.view import view_config
from isu.webapp.views import View
from glob import glob
from pprint import pprint
from pkg_resources import resource_filename
from icc.mvw.interfaces import IView, IViewRegistry
import os
import os.path
from .interfaces import IAcademicPlan
from .miis import Plan

from pyramid_storage.interfaces import IFileStorage
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("isu.college")

DATADIR = os.path.abspath(
    os.path.join(
        resource_filename(
            'isu.college',
            "../../../"),
        "data/study-plans/plans/")
)


@adapter(IAcademicPlan)
class StudyPlanVew(View):

    def __init__(self, context=None, request=None, filename=None):
        if context is not None:
            self.plan = context
        elif filename is not None:
            filename = os.path.join(DATADIR, filename)
            self.plan = Plan(filename)
        else:
            raise RuntimeError("either object or filename must be supplied")
        super(StudyPlanVew, self).__init__(context=self.plan, request=request)

    @property
    def title(self):
        # print(self.plan)
        return self.plan.program.direction

    @property
    def loc(self):
        """Return list of competence filtered.
        """
        filter = self.filter
        if filter is not None:
            yield from self.plan.show_list(
                self.plan.compl,
                filterid=filter["course"],
                form="{title} ({code})"
            )
        else:
            yield from self.plan.competence_list

    @property
    def course(self):
        if self.filter is None:
            return None
        return CourseView(self.plan.course(self.filter["course"]),
                          self.request)


class List(list):
    pass


class CourseView(View):
    """Helps represent course

    """

    def __init__(self, context, request):
        super(CourseView, self).__init__(context=context, request=request)

    def semaud(self, sem):
        def z(x):
            if x is None:
                return 0
            else:
                return x

        keys = ["lec", "pr", "lab", "iwc"]
        s = 0
        for k in keys:
            v = 0
            try:
                v = getattr(sem, k)
            except AttributeError:
                continue
            v = z(v.v)
            s += v
        return s

    @property
    def semesters(self):
        sem = []
        # print(self.context.dif.course)
        tot_aud = 0
        for ci, c in self.context.dif.course.index.items():
            c.number = ci
            for si, s in c.sem.items():
                semi = self.context.interpret(s)
                if semi.h.v is not None:
                    sem.append(semi)
                    s.number = si
                    s.course = ci
                    s.aud = self.semaud(semi)
                    tot_aud += s.aud
        sem = List(sem)
        sem.aud = tot_aud
        return sem

    def __str__(self):
        return str(self.context)


class SPListView(View):
    title = "Test"

    def __init__(self, location):
        # FIXME: Add standard arguments
        super(SPListView, self).__init__()
        self.location = os.path.abspath(location)
        template = os.path.join(location + "/*.xlsx")
        self.files = glob(template)
        self.items = set([os.path.split(fn)[-1] for fn in self.files])
        self.plan_views = {}
        # print("Location: {}".format(location))
        # print("List of plans found.")
        # pprint(self.items)

    def plan(self, name):
        if name not in self.plan_views:

            print("Loading plan:{}".format(name))
            fullpath = os.path.join(DATADIR, name)
            plan_view = self.registry.getAdapter(
                Plan(fullpath), interface=IView)
            plan_view.filename = name
            plan_view.filepathname = fullpath
            self.plan_views[name] = plan_view

        plan_view = self.plan_views[name]
        return plan_view


splistview = SPListView(DATADIR)


@view_config(route_name="plan-list", renderer="isu.college:templates/splist.pt")
def work_plans(request):
    view = request.registry.getUtility(IView, name="study-plans")
    return {
        "view": view,
    }


@view_config(route_name="plan", renderer="isu.college:templates/plan.pt")
def work_plan(request):
    md = request.matchdict
    plan_name = md["name"]
    view = request.registry.getUtility(IView, name="study-plans")

    if plan_name.endswith(".xlsx"):
        view = view.plan(plan_name)
        view.filter = None
        course = None
    else:
        parts = plan_name.split(".xlsx")
        plan_name = parts[0] + ".xlsx"
        view = view.plan(plan_name)

        course, form = (parts[1].split("-") + [None, None])[1:3]

        kwargs = {
            "course": course,
            "format": form
        }
        view.filter = kwargs
        course = view.plan.course(course)

    return {
        "view": view,
        "plan": view.plan,
    }


@view_config(route_name='commit',
             request_method='POST')
def commit(request):
    request.storage.save(request.POST['my_file'])
    return HTTPSeeOther(request.route_url('home'))


# @view_config(route_name="doc",
#              request_method="GET",
#              renderer="templates/doc.pt"
#              )
# def get_document(request):
#     return {"context": "<h1>Help!</h1>"}


class Resource(object):
    def __init__(self, name=None, parent=None):
        self.name = name
        self.parent = parent

    def __getitem__(self, name):
        if name.startswith("@@"):
            raise KeyError("wrong name")
        return Resource(name, self)

    def __str__(self):
        if self.parent is None:
            return "<root>"
        else:
            return str(self.parent) + "/" + self.name

    @property
    def pathname(self):
        s = self
        p = []
        while s is not None:
            if s.name is not None:
                p.append(s.name)
            s = s.parent
        p.reverse()
        return os.path.join(*p)

    @staticmethod
    def factory(request):
        return Resource()

# @view_config(route_name="doc",
#              request_method="GET",
#              renderer="json",
#              # name="edit"
#              )


class PageView(View):
    def __init__(self, context, request):
        super(PageView, self).__init__(context=context,
                                       request=request)
        self.message = ""
        self.result = "OK"
        self.exception = ""
        self.level = "success"
        self.content = ""

    def response(self, **kwargs):
        resp = {
            'view': self,
            'context': self.context
        }
        resp.update(kwargs)
        return resp

    def respjson(self, **kwargs):
        resp = {
            'message': self.message,
            'level': self.level,
            'result': self.result,
            'exception': self.exception,
            'content': self.content
        }
        resp.update(kwargs)
        return resp

    def failed(self, message, exception=None, level='danger'):
        self.message = message
        self.exception = '' if exception is None else str(exception)
        self.level = level
        self.result = "KO"
        return self.response()

    def __call__(self):
        methodnamebase = "route_" + self.name
        methodname = methodnamebase + "_" + self.request.method.lower()
        while True:
            if hasattr(self, methodname):
                method = getattr(self, methodname)
                return method()
            if methodname == methodnamebase:
                break
            methodname = methodnamebase

        raise RuntimeError("Not implemented")

    @property
    def name(self):
        return self.request.view_name

    def pathname(self, split=False, all=False):
        pname = self.context.pathname.strip()
        if all:
            split = True
        if split:
            fn, ext = os.path.splitext(pname)
            if not all:
                return fn, ext
        if all:
            return pname, self.storage.path(pname), fn, ext

        return pname

    @property
    def storage(self):
        return self.request.storage

    def main_loader(self):
        filename, physfn, fn, ext = self.pathname(all=True)

        if ext.lower() in [".html", ".xhtml"]:
            try:
                self.content = open(physfn).read()
                self.message = _("Successfully loaded")
                return self.response()
            except Exception as e:
                return self.failed(
                    _("Cannot load page. It seems it does not exist."),
                    exception=e
                )
        else:
            return FileResponse(physfn)

    def route_content_get(self):
        filename, physfn, fn, ext = self.pathname(all=True)
        return FileResponse(physfn)

    def route_save_post(self):
        filename, physfn, fn, ext = self.pathname(all=True)
        print(filename, physfn, fn, ext)
        self.message = "Fake save"
        body_file = self.request.body_file
        self.storage.save_file(body_file, filename, replace=True)

        return self.respjson()


#@adapter(IConfigurationEvent)


def configurator(config, **settings):
    config.load_zcml("isu.college:configure.zcml")

    config.add_route("plan", "/plan/{name}.html")
    config.add_route("plan-list", "/plan/")
    config.add_route("commit",    "/api/v1/commit")
    config.add_route("branch", "/api/v1/branch")

    #config.add_static_view(name='/lcss', path='isu.college:templates/lcss')

    storage = config.registry.getUtility(IFileStorage)
    try:
        static_dir = config.registry.settings["storage.static"]
    except KeyError:
        raise RuntimeError("storage.static settings needed")

    static_dir = os.path.join(storage.base_path, static_dir)
    static_dir = os.path.abspath(static_dir)

    for d in os.listdir(static_dir):
        config.add_static_view(name='/' + d, path=os.path.join(static_dir, d))

    config.add_subscriber('isu.college.subscribers.add_base_template',
                          'pyramid.events.BeforeRender')
    config.scan()

    config.add_route("doc", "/*traverse", factory=Resource.factory)
    config.add_view(view=PageView,
                    attr="main_loader",
                    route_name="doc",
                    renderer="templates/doc.pt",
                    request_method="GET")
    config.add_view(view=PageView,
                    route_name="doc",
                    name="content",
                    request_method="GET")
    config.add_view(view=PageView,
                    route_name="doc",
                    renderer="json",
                    name="save",
                    request_method="POST")
    config.add_view(view=PageView,
                    route_name="doc",
                    renderer="json",
                    name="commit",
                    request_method="POST")
    # config.add_view(view=test_edit, route_name="doc",
    #                 name="edit",
    #                 renderer="json",
    #                 )


def zcml(config):
    """Runs zcml configuration on the
    config object.
    FIXME: Get rid of this (zcml(..)) shame stauff. ;-)
    """
    # print("REG---------------")
    # print(list(config.registry.registeredSubscriptionAdapters()))
    config.add_subscriber(configurator, IConfigurationEvent)
