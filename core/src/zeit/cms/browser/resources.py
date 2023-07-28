from fanstatic import Library, Group
from js.jquery import jquery
from js.mochikit import mochikit
from js.select2 import select2_de
from js.underscore import underscore
from js.vanderlee_colorpicker import colorpicker
import fanstatic
import importlib.resources
import js.jqueryui
import os.path
import sys


lib_css = Library('zeit.cms', 'resources')
lib_js = Library('zeit.cms.js', 'js')

backend = Group([])


def register(resource):
    depends = backend.depends.union(
        set([resource]))
    for dep in depends:
        backend.resources.update(dep.resources)


class Resource(fanstatic.Resource):

    def __init__(self, filename, *args, **kw):
        globs = kw.pop('globs', sys._getframe(1).f_globals)
        lib = kw.pop('lib', globs.get('lib'))
        super().__init__(lib, filename, *args, **kw)
        globs['%s_%s' % self.splitext(filename)] = self
        register(self)

    def splitext(self, path):
        base, ext = os.path.splitext(os.path.basename(path))
        type_ = ext[1:]
        return base, type_


class SplitDirResource(Resource):

    def __init__(self, filename, *args, **kw):
        base, type_ = self.splitext(filename)
        kw['globs'] = sys._getframe(1).f_globals
        kw['lib'] = kw['globs']['lib_%s' % type_]
        super().__init__(filename, *args, **kw)


SplitDirResource('forms.css')
SplitDirResource('tables.css')
SplitDirResource('lightbox.css')
SplitDirResource('cms_widgets.css')
SplitDirResource('object_details.css')
SplitDirResource('cms.css')

# Only explicitly included by .login.Login
login_css = fanstatic.Resource(lib_css, 'login.css')

jqueryui_theme = fanstatic.Resource(
    lib_js, 'jquery/jquery-ui-custom-theme/jquery-ui-1.10.4.custom.css',
    minified='jquery/jquery-ui-custom-theme/jquery-ui-1.10.4.custom.min.css')
jqueryui = fanstatic.Group([js.jqueryui.jqueryui, jqueryui_theme])
register(jqueryui)

zc_table = Library(
    'zc.table', str((importlib.resources.files('zc.table') / 'resources')))
zc_table_js = fanstatic.Resource(zc_table, 'sorting.js')
register(zc_table_js)


zc_datetimewidget = Library(
    'zc.datetimewidget', str((importlib.resources.files(
        'zc.datetimewidget') / 'resources')))
datetime_css = fanstatic.Resource(zc_datetimewidget, 'calendar-system.css')
datetime_calendar_js = fanstatic.Resource(zc_datetimewidget, 'calendar.js')
datetime_calendar_setup_js = fanstatic.Resource(
    zc_datetimewidget, 'calendar-setup.js', depends=[datetime_calendar_js])
datetime_calendar_en_js = fanstatic.Resource(
    zc_datetimewidget, 'languages/calendar-en.js',
    depends=[datetime_calendar_js])
datetime_widget_js = fanstatic.Resource(
    zc_datetimewidget, 'datetimewidget.js', depends=[
        datetime_css, datetime_calendar_en_js, datetime_calendar_setup_js,
    ])
register(datetime_widget_js)


SplitDirResource('namespace.js')
SplitDirResource('logging.js', depends=[namespace_js, mochikit, jquery])  # noqa
SplitDirResource('draganddrop.js', depends=[mochikit])
SplitDirResource('base.js', depends=[
    namespace_js, draganddrop_js, mochikit, jquery, jqueryui,   # noqa
    underscore, select2_de])

base = Group([
    namespace_js, logging_js, base_js,  # noqa
    cms_css, forms_css, tables_css, lightbox_css,  # noqa
    cms_widgets_css, object_details_css,  # noqa
])

SplitDirResource('objectbrowser.js', depends=[base])
SplitDirResource('tooltip.js', depends=[base])
SplitDirResource('view.js', depends=[base])
SplitDirResource('form.js', depends=[view_js, base])  # noqa
SplitDirResource('lightbox.js', depends=[form_js, base])  # noqa
SplitDirResource('counter.js', depends=[base])
SplitDirResource('details.js', depends=[base])
SplitDirResource('dnd.js', depends=[base])
SplitDirResource('object_reference.js', depends=[lightbox_js, base])  # noqa
SplitDirResource('object_sequence.js', depends=[base])
SplitDirResource('restructuredtext.js', depends=[base])
SplitDirResource('autocomplete.js', depends=[base])
SplitDirResource('colorpicker.js', depends=[base, colorpicker])
SplitDirResource('table.js', depends=[base])
SplitDirResource('xeyes.js', depends=[base])
SplitDirResource('menu.js', depends=[base])
SplitDirResource('json-template.js', depends=[base])
SplitDirResource('messages.js', depends=[base, view_js])  # noqa
SplitDirResource('tab.js', depends=[base, view_js])  # noqa
SplitDirResource('tree.js', depends=[base])
SplitDirResource('filteringtable.js', depends=[base])
SplitDirResource('panelHandlers.js', depends=[base])
SplitDirResource('filename.js', depends=[base])
SplitDirResource('bullet.js', depends=[base])
SplitDirResource('formlib.js')
