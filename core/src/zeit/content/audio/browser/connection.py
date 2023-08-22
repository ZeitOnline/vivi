import zeit.cms.browser.view
import zeit.content.audio.interfaces


class Status:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def has_permission(self, permission):
        return self.request.interaction.checkPermission(
            permission, self.context)


class Request(zeit.cms.browser.view.Base):

    def __call__(self):
        zeit.simplecast.interfaces.IConnector(self.context)
        return self.redirect(self.url('simplecast.html'))
