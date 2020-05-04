from zeit.cms.i18n import MessageFactory as _
import base64
import six.moves.urllib.parse
import zeit.cms.browser.view
import zeit.edit.browser.view
import zeit.edit.interfaces
import zope.security.proxy


class History(zeit.cms.browser.view.JSON):

    resource_library = 'zeit.edit'
    template = 'history.jsont'

    def json(self):
        history = zeit.edit.interfaces.IUndo(
            zope.security.proxy.getObject(self.context)).history
        for entry in history:
            if entry['description'] is None:
                entry['description'] = '[none]'
            entry['tid'] = six.moves.urllib.parse.quote(base64.b64encode(
                entry['tid']).decode('ascii'))

        return {
            'context_url': self.url(self.context),
            'history': history,
        }


class Revert(zeit.edit.browser.view.Action):

    tid = zeit.edit.browser.view.Form('tid')

    def update(self):
        tid = base64.b64decode(six.moves.urllib.parse.unquote(
            self.tid).encode('ascii'))
        undo = zeit.edit.interfaces.IUndo(
            zope.security.proxy.getObject(self.context))

        for entry in undo.history:
            if entry['tid'] == tid:
                self.undo_description = _(
                    'revert up to "${action}"', mapping=dict(
                        action=entry['description']))
                break

        undo.revert(tid)
        self.signal(None, 'reload-editor')
