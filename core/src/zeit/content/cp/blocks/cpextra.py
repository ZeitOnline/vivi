import grokcore.component as grok
import lxml.objectify

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


@grok.subscribe(
    zeit.content.cp.interfaces.ICenterPage, zeit.cms.checkout.interfaces.IAfterCheckoutEvent
)
def update_old_cpextras(context, event):
    for cp_extra in context.xml.xpath(
        '//container[@cp:type != "cpextra"]/cp_extra',
        namespaces={'cp': 'http://namespaces.zeit.de/CMS/cp'},
    ):
        cp_extra.getparent().set('{http://namespaces.zeit.de/CMS/cp}type', 'cpextra')
