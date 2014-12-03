# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.edit.rule import glob
import itertools
import zeit.content.cp.interfaces
import zope.component
import zope.interface


class CenterPageValidator(zeit.edit.rule.RecursiveValidator):

    zope.component.adapts(zeit.content.cp.interfaces.ICenterPage)

    @property
    def children(self):
        areas = self.context.values()
        return itertools.chain(areas, *[a.values() for a in areas])


@glob(zeit.edit.interfaces.IElement)
def section(context):
    return zeit.content.cp.interfaces.ISection(context).__name__


@glob(zeit.content.cp.interfaces.ISection)
def area(context):
    # emergency brake, since otherwise sections don't know they were formely an
    # area and would forward the question to their parent, which is a
    # CenterPage, which asks their parent, which will trigger an adapter to
    # AutomaticRegion which is ... not what we want in any case ever
    return None # context.__name__


@glob(zeit.content.cp.interfaces.ITeaserBar)
def area(context):
    return context.__parent__.__name__


@glob(zeit.content.cp.interfaces.IRegion)
def is_region(context):
    return True


@glob(zope.interface.Interface)
def is_region(context):
    return False


@glob(zeit.content.cp.interfaces.ITeaserBlock)
def layout(context):
    return context.layout.id


@glob(zeit.content.cp.interfaces.ITeaserBar)
def layout(context):
    return context.layout.id


@glob(zope.interface.Interface)
def layout(context):
    return None


@glob(zeit.content.cp.interfaces.IBlock)
def content(context):
    return list(
        zeit.content.cp.interfaces.ICMSContentIterable(context, []))


@glob(zope.interface.Interface)
def cp_type(context):
    cp = zeit.content.cp.interfaces.ICenterPage(context, None)
    if cp is None:
        return None
    return cp.type
