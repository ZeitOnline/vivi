# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.interfaces
import zeit.cms.tagging.interfaces
import zope.container.btree
import zope.interface


class Whitelist(zope.container.btree.BTreeContainer):

    # XXX this is only a toy implementation, see #8624
    # add tags for testing like this:
    # whitelist['mytag'] = zeit.cms.tagging.tag.Tag('mytag')

    zope.interface.implements(zeit.cms.tagging.interfaces.IWhitelist)

    def search(self, prefix):
        result = []
        for tag in self.values():
            if tag.label.lower().startswith(prefix.lower()):
                result.append(tag)
        return result


class WhitelistSource(object):

    # this should be in .interfaces, but that leads to a circular import
    # between zeit.cms.content.interfaces and .interfaces

    zope.interface.implements(
        zeit.cms.tagging.interfaces.IWhitelistSource,
        zeit.cms.content.interfaces.IAutocompleteSource)

    @property
    def whitelist(self):
        return zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)

    def __contains__(self, item):
        return item.code in self.whitelist

    def __iter__(self):
        return iter(self.whitelist.values())

    def get_check_types(self):
        return ['tag']
