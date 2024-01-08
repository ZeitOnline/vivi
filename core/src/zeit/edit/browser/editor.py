from zope.browserpage import ViewPageTemplateFile

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.view


class Editor(zeit.cms.browser.view.Base):
    render = ViewPageTemplateFile('editor.pt')
    title = _('Edit')
