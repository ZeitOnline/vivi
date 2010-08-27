# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import datetime
import gocept.runner
import grokcore.component
import persistent
import pytz
import zeit.cms.content.interfaces
import zeit.cms.related.interfaces
import zeit.cms.type
import zeit.content.cp.teasergroup.interfaces
import zeit.content.image.interfaces
import zope.component
import zope.container.btree
import zope.container.contained
import zope.container.interfaces
import zope.index.text.interfaces
import zope.interface
import zope.keyreference.interfaces


class TeaserGroup(persistent.Persistent,
                  zope.container.contained.Contained):

    zope.interface.implements(
        zeit.content.cp.teasergroup.interfaces.ITeaserGroup)

    automatically_remove = True
    name = None
    uniqueId = None
    _teasers = ()

    @property
    def teasers(self):
        return tuple(ref() for ref in self._teasers)

    @teasers.setter
    def teasers(self, value):
        self._teasers = tuple(
            zope.keyreference.interfaces.IKeyReference(v) for v in value)

    def create(self):
        repository = zope.component.getUtility(
            zeit.content.cp.teasergroup.interfaces.IRepository)
        repository.add(self)


class TeaserGroupType(zeit.cms.type.TypeDeclaration):

    interface = zeit.content.cp.teasergroup.interfaces.ITeaserGroup
    title = _('Teasergroup')


class SemanticChange(grokcore.component.Adapter):

    grokcore.component.context(
        zeit.content.cp.teasergroup.interfaces.ITeaserGroup)
    grokcore.component.implements(
        zeit.cms.content.interfaces.ISemanticChange)

    @property
    def last_semantic_change(self):
        dc = zope.dublincore.interfaces.IDCTimes(self.context)
        return dc.modified

    @last_semantic_change.setter
    def last_semantic_change(self, value):
        dc = zope.dublincore.interfaces.IDCTimes(self.context)
        dc.modified = value


class Related(grokcore.component.Adapter):

    grokcore.component.context(
        zeit.content.cp.teasergroup.interfaces.ITeaserGroup)
    grokcore.component.implements(
        zeit.cms.related.interfaces.IRelatedContent)

    @property
    def related(self):
        return self.context.teasers


@grokcore.component.adapter(
    zeit.content.cp.teasergroup.interfaces.ITeaserGroup)
@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
def images(context):
    assert context.teasers
    return zeit.content.image.interfaces.IImages(context.teasers[0], None)


class SearchableText(grokcore.component.Adapter):

    grokcore.component.context(
        zeit.content.cp.teasergroup.interfaces.ITeaserGroup)
    grokcore.component.implements(
        zope.index.text.interfaces.ISearchableText)

    def getSearchableText(self):
        result = [self.context.name]
        for teaser in self.context.teasers:
            searchable_text = zope.index.text.interfaces.ISearchableText(
                teaser, None)
            if searchable_text is None:
                continue
            result.extend(searchable_text.getSearchableText())
        return result


class Repository(zope.container.btree.BTreeContainer):

    zope.interface.implements(
            zeit.content.cp.teasergroup.interfaces.IRepository)

    AUTOREMOVE_AFTER = datetime.timedelta(days=7)

    def add(self, teasergroup):
        assert zeit.content.cp.teasergroup.interfaces.ITeaserGroup.providedBy(
            teasergroup)
        chooser = zope.container.interfaces.INameChooser(self)
        name = chooser.chooseName(teasergroup.name, teasergroup)
        self[name] = teasergroup
        teasergroup.uniqueId = (
            zeit.content.cp.teasergroup.interfaces.ID_NAMESPACE + name)

    def sweep(self):
        remove = []
        now = datetime.datetime.now(pytz.UTC)
        for name, group in self.items():
            if not group.automatically_remove:
                continue
            dc = zope.dublincore.interfaces.IDCTimes(group)
            if dc.created + self.AUTOREMOVE_AFTER < now:
                remove.append(name)
        for name in remove:
            del self[name]


@gocept.runner.once()
def sweep_repository():
    repository = zope.component.getUtility(
        zeit.content.cp.teasergroup.interfaces.IRepository)
    repository.sweep()


@grokcore.component.adapter(
    basestring, name=zeit.content.cp.teasergroup.interfaces.ID_NAMESPACE)
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContent)
def unique_id_toteasergroup(unique_id):
    assert unique_id.startswith(
        zeit.content.cp.teasergroup.interfaces.ID_NAMESPACE)
    name = unique_id.replace(
        zeit.content.cp.teasergroup.interfaces.ID_NAMESPACE, '', 1)
    repository = zope.component.getUtility(
        zeit.content.cp.teasergroup.interfaces.IRepository)
    return repository.get(name)
