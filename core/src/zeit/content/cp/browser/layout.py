import grokcore.component as grok
import zc.resourcelibrary.resourcelibrary
import zope.interface
import zope.publisher.interfaces.browser


class RemoteURLResourceDirectory(grok.Adapter):

    grok.context(zope.publisher.interfaces.browser.IDefaultBrowserLayer)
    grok.provides(zope.interface.Interface)
    grok.name('zeit.content.cp.layout')

    def __getitem__(self, filename):
        request = self.context
        return lambda: '%s/repository/data/cp-layouts/%s/@@raw.css' % (
            request.getApplicationURL(), filename)


lib = zc.resourcelibrary.resourcelibrary.LibraryInfo()
lib.included.append('layouts.css')
zc.resourcelibrary.resourcelibrary.library_info['zeit.content.cp.layout'] = lib


class RawCSS(object):

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/css')
        return self.context.data
