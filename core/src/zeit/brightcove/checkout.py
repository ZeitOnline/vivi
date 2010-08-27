# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import grokcore.view
import zeit.brightcove.content
import zeit.brightcove.interfaces
import zeit.cms.checkout.interfaces
import zope.component
import zope.security.proxy


@grokcore.component.adapter(zeit.brightcove.interfaces.IVideo)
@grokcore.component.implementer(zeit.cms.checkout.interfaces.ILocalContent)
def local_video(context):
    video = zeit.brightcove.content.Video(
        zope.security.proxy.removeSecurityProxy(context).data)
    zope.interface.alsoProvides(
        video, zeit.cms.workingcopy.interfaces.ILocalContent)
    return video


@grokcore.component.adapter(zeit.brightcove.interfaces.IVideo)
@grokcore.component.implementer(
    zeit.cms.checkout.interfaces.IRepositoryContent)
def repository_video(context):
    video = zeit.brightcove.content.Video(
        zope.security.proxy.removeSecurityProxy(context).data)
    repository = zope.component.getUtility(
        zeit.brightcove.interfaces.IRepository)
    repository[video.__name__] = video
    video.__parent__ = repository
    video.save_to_brightcove()
    return video


class CheckoutMenuItem(object):

    sort = 0

    def render(self):
        # We don't want an item, so provide one which renders itself empty.
        return u''


class Edit(grokcore.view.View):

    grokcore.view.context(zeit.brightcove.interfaces.IVideo)
    grokcore.view.name('edit.html')

    def render(self):
        self.redirect(self.url(''))
