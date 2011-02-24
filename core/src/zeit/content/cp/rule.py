# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import itertools
import zeit.cms.workflow.interfaces
import zeit.content.cp.interfaces
import zeit.edit.rule
import zeit.workflow.timebased
import zope.component
import zope.interface


@zeit.edit.rule.glob(zeit.edit.interfaces.IElement)
def position(context):
    return context.__parent__.keys().index(context.__name__) + 1


@zeit.edit.rule.glob(zeit.edit.interfaces.IElement)
def area(context):
    return zeit.edit.interfaces.IArea(context).__name__


@zeit.edit.rule.glob(zeit.content.cp.interfaces.IBlock)
def type(context):
    return context.type


@zeit.edit.rule.glob(zeit.content.cp.interfaces.IBlock)
def is_block(context):
    return True


@zeit.edit.rule.glob(zope.interface.Interface)
def is_block(context):
    return False


@zeit.edit.rule.glob(zeit.edit.interfaces.IArea)
def is_area(context):
    return True


@zeit.edit.rule.glob(zope.interface.Interface)
def is_area(context):
    return False


@zeit.edit.rule.glob(zope.interface.Interface)
def is_region(context):
    return False


@zeit.edit.rule.glob(zeit.content.cp.interfaces.IRegion)
def is_region(context):
    return True


@zeit.edit.rule.glob(zeit.edit.interfaces.IContainer)
def count(context):
    return len(context)


@zeit.edit.rule.glob(zeit.content.cp.interfaces.ITeaserBlock)
def layout(context):
    return context.layout.id


@zeit.edit.rule.glob(zeit.content.cp.interfaces.ITeaserBar)
def layout(context):
    return context.layout.id


@zeit.edit.rule.glob(zeit.content.cp.interfaces.IBlock)
def content(context):
    return list(
        zeit.content.cp.interfaces.ICMSContentIterable(context, []))


@zeit.edit.rule.glob(zope.interface.Interface)
def cp_type(context):
    cp = zeit.content.cp.interfaces.ICenterPage(context, None)
    if cp is None:
        return None
    return cp.type


@zeit.edit.rule.glob(zope.interface.Interface)
def is_published(context):
    def is_published_inner(obj):
        pi = zeit.cms.workflow.interfaces.IPublishInfo(obj, None)
        return pi is not None and pi.published
    return is_published_inner


class CenterPageValidator(zeit.edit.rule.RecursiveValidator):

    zope.component.adapts(zeit.content.cp.interfaces.ICenterPage)

    @property
    def children(self):
        areas = self.context.values()
        return itertools.chain(areas, *[a.values() for a in areas])


class ValidatingWorkflow(zeit.workflow.timebased.TimeBasedWorkflow):

    def can_publish(self):
        validator = zeit.edit.interfaces.IValidator(self.context)
        if validator.status == zeit.edit.rule.ERROR:
            return False
        return True
