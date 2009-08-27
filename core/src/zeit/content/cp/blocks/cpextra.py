# coding: utf8
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.objectify
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.component
import zope.container.interfaces
import zope.interface


class CPExtraBlock(zeit.content.cp.blocks.block.Block):


    zope.interface.implements(zope.container.interfaces.IContained,
                              zeit.content.cp.interfaces.ICPExtraBlock)


class CPExtraBlockFactory(zeit.content.cp.blocks.block.ElementFactory):


    def get_xml(self):
        xml = super(CPExtraBlockFactory, self).get_xml()
        xml.append(lxml.objectify.E.cp_extra(id=self.element_type))
        return xml


cp_extras = []

def factor(extra_id, title, interface=zeit.content.cp.interfaces.IRegion):
    """A factory which creates a cpextra block and a corresponding factory."""
    class_name = '%sBlock' % extra_id.capitalize()
    class_ = type(class_name, (CPExtraBlock,), dict(
        block_title=title))

    factory_name = '%sFactory' % extra_id.capitalize()
    factory = type(factory_name, (CPExtraBlockFactory,), dict(
        title=title,
        element_class=class_,
        element_type=extra_id,
        module=extra_id))
    factory = zope.component.adapter(interface)(factory)

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
        zeit.content.cp.interfaces.IElementFactory, name='mostread')()
    zope.component.getAdapter(
        context['informatives'],
        zeit.content.cp.interfaces.IElementFactory, name='mostcommented')()


factor('mostread', u'Meistgelesen',
       zeit.content.cp.interfaces.IInformatives)
factor('mostcommented', u'Meistkommentiert',
       zeit.content.cp.interfaces.IInformatives)
factor('weather', u'Wetter')
factor('stocks', u'Börse')
factor('ressort_news', u'Neu Im Ressort',
       zeit.content.cp.interfaces.IInformatives)
factor('live_search', u'Live-Search',
       zeit.content.cp.interfaces.IInformatives)
factor('print_archive', u'Print Archiv',
       zeit.content.cp.interfaces.IInformatives)
factor('blindblock', u'Blindblock',
       zeit.content.cp.interfaces.IInformatives)
factor('homepage_news', u'Neu auf Zeit Online')
factor('dpa-news', u'dpa-News')
