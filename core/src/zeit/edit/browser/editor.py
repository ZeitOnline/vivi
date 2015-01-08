from zeit.cms.i18n import MessageFactory as _
from zope.browserpage import ViewPageTemplateFile


class Editor(object):

    render = ViewPageTemplateFile('editor.pt')
    title = _('Edit')
