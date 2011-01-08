# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import sys
import transaction
import zeit.cms.interfaces
import zeit.cms.relation.interfaces
import zeit.cms.testing
import zope.component
import zope.site.hooks


# these are 'zopectl run' scripts to migrate the old indexes into the new index
# created for #6300.


def dump_references(root):
    zope.site.hooks.setSite(root)
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    for token in relations._catalog_generation8.findRelationTokens():
        print token.encode('utf8')


def load_references(root):
    zeit.cms.testing.create_interaction(u'zope.manager')
    _index(root, [x.strip() for x in sys.stdin.readlines()])


def _index(root, ids):
    zope.site.hooks.setSite(root)
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    for id in ids:
        print id,
        id = unicode(id, 'utf8')
        obj = zeit.cms.interfaces.ICMSContent(id, None)
        if obj is None:
            print "not found."
            continue
        relations.index(obj)
        transaction.commit()
        print "indexed."
