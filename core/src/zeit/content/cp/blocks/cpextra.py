import grokcore.component as grok
import lxml.objectify
import zope.component

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.checkout.interfaces
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces


@grok.implementer(zeit.content.cp.interfaces.ICPExtraBlock)
class CPExtraBlock(zeit.content.cp.blocks.block.Block):
    type = 'cpextra'

    @property
    def cpextra(self):
        return self.xml.get('module')

    @cpextra.setter
    def cpextra(self, value):
        self.xml.set('module', value)
        self.xml['cp_extra'] = lxml.objectify.E.cp_extra(id=value)


class Factory(zeit.content.cp.blocks.block.BlockFactory):
    produces = CPExtraBlock
    title = _('CP extra')
    module = ''


# This method only applies to "old" (lead/informatives/mosaic) centerpages
@grok.subscribe(
    zeit.content.cp.interfaces.ICenterPage, zeit.cms.repository.interfaces.IBeforeObjectAddEvent
)
def add_blocks_to_newly_created_cp(context, event):
    # The BeforeObjectAddEvent is sent whenever an object is added or changed.
    # We need to check if this is the first add or not.
    if zeit.cms.interfaces.ICMSContent(context.uniqueId, None) is not None:
        # It's already in the repository, do nothing
        return
    if 'informatives' not in context:
        # It's a new-style centerpage, do nothing
        return
    mostread = zope.component.getAdapter(
        context['informatives'], zeit.edit.interfaces.IElementFactory, name='cpextra'
    )()
    mostread.cpextra = 'mostread'
    mostcommented = zope.component.getAdapter(
        context['informatives'], zeit.edit.interfaces.IElementFactory, name='cpextra'
    )()
    mostcommented.cpextra = 'mostcommented'


@grok.subscribe(
    zeit.content.cp.interfaces.ICenterPage, zeit.cms.checkout.interfaces.IAfterCheckoutEvent
)
def update_old_cpextras(context, event):
    for cp_extra in context.xml.xpath(
        '//container[@cp:type != "cpextra"]/cp_extra',
        namespaces={'cp': 'http://namespaces.zeit.de/CMS/cp'},
    ):
        cp_extra.getparent().set('{http://namespaces.zeit.de/CMS/cp}type', 'cpextra')
