# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import lxml.objectify
import zeit.cms.checkout.interfaces
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.component
import zope.container.interfaces
import zope.interface


class CPExtraBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zope.container.interfaces.IContained,
                              zeit.content.cp.interfaces.ICPExtraBlock)

    @property
    def cpextra(self):
        return self.xml.get('module')

    @cpextra.setter
    def cpextra(self, value):
        self.xml.set('module', value)
        self.xml['cp_extra'] = lxml.objectify.E.cp_extra(id=value)


zeit.edit.block.register_element_factory(
    zeit.content.cp.interfaces.IRegion, 'cpextra', _('CP extra'), module='')


@grokcore.component.subscribe(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.repository.interfaces.IBeforeObjectAddEvent)
def add_blocks_to_newly_created_cp(context, event):
    # The BeforeObjectAddEvent is sent whenever an object is added or changed.
    # We need to check if this is the first add or not.
    if zeit.cms.interfaces.ICMSContent(context.uniqueId, None) is not None:
        # It's already in the repository, do nothing
        return
    mostread = zope.component.getAdapter(
        context['informatives'],
        zeit.edit.interfaces.IElementFactory, name='cpextra')()
    mostread.cpextra = 'mostread'
    mostcommented = zope.component.getAdapter(
        context['informatives'],
        zeit.edit.interfaces.IElementFactory, name='cpextra')()
    mostcommented.cpextra = 'mostcommented'


@grokcore.component.subscribe(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def update_old_cpextras(context, event):
    for cp_extra in context.xml.xpath(
        '//container[@cp:type != "cpextra"]/cp_extra',
        namespaces={'cp': 'http://namespaces.zeit.de/CMS/cp'}):
        cp_extra.getparent().set('{http://namespaces.zeit.de/CMS/cp}type',
                                 'cpextra')
