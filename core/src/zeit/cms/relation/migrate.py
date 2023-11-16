import sys
import transaction
import zeit.cms.interfaces
import zeit.cms.relation.interfaces
import zope.component
import zope.component.hooks


# these are 'zopectl run' scripts to migrate the old indexes into the new index
# created for #6300.


def dump_references(root):
    zope.component.hooks.setSite(root)
    relations = zope.component.getUtility(zeit.cms.relation.interfaces.IRelations)
    for token in relations._catalog_generation8.findRelationTokens():
        print((token.encode('utf8')))


def load_references(root):
    import zeit.cms.testing

    zeit.cms.testing.create_interaction('zope.manager')
    _index(root, [x.strip() for x in sys.stdin.readlines()])


def _index(root, ids):
    zope.component.hooks.setSite(root)
    relations = zope.component.getUtility(zeit.cms.relation.interfaces.IRelations)
    for id in ids:
        print(id)
        id = id.decode('utf-8')
        obj = zeit.cms.interfaces.ICMSContent(id, None)
        if obj is None:
            print('not found.')
            continue
        relations.index(obj)
        transaction.commit()
        print('indexed.')
