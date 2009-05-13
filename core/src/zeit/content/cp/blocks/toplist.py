# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import lxml.objectify
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.component
import zope.container.interfaces
import zope.interface


class MostRead(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(
        zeit.content.cp.interfaces.IMostReadBlock,
        zope.container.interfaces.IContained)



class MostReadFactory(zeit.content.cp.blocks.block.BlockFactory):


    zope.component.adapts(zeit.content.cp.interfaces.IRegion)

    block_class = MostRead
    block_type = 'mostread'
    title = _('Most read block')

    def get_xml(self):
        xml = super(type(self), self).get_xml()
        xml.append(lxml.objectify.E.cp_extra(id='mostread'))
        return xml


@zope.component.adapter(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.repository.interfaces.IBeforeObjectAddEvent)
def add_mostread_to_newly_created_cp(context, event):
    # The BeforeObjectAddEvent is sent whenever an object is added or changed.
    # We need to check if this is the first add or not.
    if zeit.cms.interfaces.ICMSContent(context.uniqueId, None) is not None:
        # It's already in the repository, do nothing
        return
    factory = zope.component.getAdapter(
        context['informatives'],
        zeit.content.cp.interfaces.IBlockFactory, name='mostread')
    factory()
