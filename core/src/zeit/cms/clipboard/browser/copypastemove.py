# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
import zope.component

import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.cms.clipboard.interfaces
import zeit.cms.repository.interfaces
from zeit.cms.i18n import MessageFactory as _


class InsertMenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):
    """Insert menu item."""

    title = _('Copy from clipboard')
    icon = '/@@/zeit.cms/icons/insert.png'


class InsertLightbox(object):

    @zope.cachedescriptors.property.Lazy
    def clipboard(self):
        return zeit.cms.clipboard.interfaces.IClipboard(self.request.principal)

    @zope.cachedescriptors.property.Lazy
    def uniqueId(self):
        return self.context.uniqueId



class Insert(zeit.cms.browser.view.Base):
    """Insert object from clipboard into current container."""

    def __call__(self, unique_id):
        source = self.repository.getContent(unique_id)
        copier = zope.copypastemove.interfaces.IObjectCopier(source)
        new_name = copier.copyTo(self.context)
        new_obj = self.context[new_name]
        self.send_message(
            _('${source} was copied to ${target}.',
              mapping=dict(
                  source=unique_id,
                  target=new_obj.uniqueId)))
        self.redirect(self.url(new_obj))

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
