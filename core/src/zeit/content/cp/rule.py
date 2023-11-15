from zeit.edit.rule import glob
import itertools
import zeit.content.cp.interfaces
import zeit.edit.interfaces
import zope.component
import zope.interface


@zope.component.adapter(zeit.content.cp.interfaces.ICenterPage)
class CenterPageValidator(zeit.edit.rule.RecursiveValidator):
    @property
    def children(self):
        # WARNING: Does not include modules, only regions and areas.
        # Therefore rules for modules aren't executed.
        areas = self.context.values()
        return itertools.chain(areas, *[a.values() for a in areas])


@glob(zeit.content.cp.interfaces.IRegion)
def is_region(context):
    return True


@glob(zope.interface.Interface)
def is_region(context):  # noqa
    return False


@glob(zeit.content.cp.interfaces.IElement)
def region(context):
    return zeit.content.cp.interfaces.IRegion(context).__name__


@glob(zope.interface.Interface)
def region(context):  # noqa
    return None


@glob(zeit.content.cp.interfaces.ITeaserBlock)
def layout(context):
    return context.layout.id


@glob(zope.interface.Interface)
def layout(context):  # noqa
    return None


@glob(zeit.content.cp.interfaces.IBlock)
def content(context):
    return list(zeit.edit.interfaces.IElementReferences(context, []))


@glob(zope.interface.Interface)
def cp_type(context):
    cp = zeit.content.cp.interfaces.ICenterPage(context, None)
    if cp is None:
        return None
    return cp.type


@glob(zope.interface.Interface)
def centerpage(context):
    cp = zeit.content.cp.interfaces.ICenterPage(context, None)
    if cp is None:
        return None
    return cp


@glob(zeit.content.cp.interfaces.IBlock)
def all_modules(context):
    cp = zeit.content.cp.interfaces.ICenterPage(context, None)
    if cp is None:
        return iter([])

    def inner():
        for region in cp.values():
            for area in region.values():
                for module in area.values():
                    yield module

    return inner()
