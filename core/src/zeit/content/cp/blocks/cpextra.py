# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import lxml.objectify
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.component
import zope.container.interfaces
import zope.interface


class CPExtraBlock(zeit.content.cp.blocks.block.Block):


    zope.interface.implements(zope.container.interfaces.IContained,
                              zeit.content.cp.interfaces.ICPExtraBlock)


class CPExtraBlockFactory(zeit.content.cp.blocks.block.BlockFactory):


    def get_xml(self):
        xml = super(CPExtraBlockFactory, self).get_xml()
        xml.append(lxml.objectify.E.cp_extra(id=self.block_type))
        return xml


cp_extras = []

def factor(extra_id, title):
    """A factory which creates a cpextra block and a corresponding factory."""
    class_name = '%sBlock' % extra_id.capitalize()
    class_ = type(class_name, (CPExtraBlock,), dict(
        title=title))

    factory_name = '%sFactory' % extra_id.capitalize()
    factory = type(factory_name, (CPExtraBlockFactory,), dict(
        title=title,
        block_class=class_,
        block_type=extra_id))
    factory = zope.component.adapter(
        zeit.content.cp.interfaces.IRegion)(factory)

    globals()[class_name] = class_
    globals()[factory_name] = factory
    cp_extras.append((class_, factory, extra_id))


@zope.component.adapter(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.repository.interfaces.IBeforeObjectAddEvent)
def add_blocks_to_newly_created_cp(context, event):
    # The BeforeObjectAddEvent is sent whenever an object is added or changed.
    # We need to check if this is the first add or not.
    if zeit.cms.interfaces.ICMSContent(context.uniqueId, None) is not None:
        # It's already in the repository, do nothing
        return
    zope.component.getAdapter(
        context['informatives'],
        zeit.content.cp.interfaces.IBlockFactory, name='mostread')()
    zope.component.getAdapter(
        context['informatives'],
        zeit.content.cp.interfaces.IBlockFactory, name='mostcommented')()


factor('mostread', u'Meistgelesen')
factor('mostcommented', u'Meistkommentiert')
