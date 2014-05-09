# Copyright (c) 2014 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.edit.rule import glob
import zeit.cms.interfaces
import zeit.newsletter.interfaces
import zope.component
import zope.interface


class NewsletterValidator(zeit.edit.rule.RecursiveValidator):

    zope.component.adapts(zeit.newsletter.interfaces.INewsletter)

    @property
    def children(self):
        return self.context.body.values()


def get_newsletter(candidate):
    while candidate is not None:
        if zeit.newsletter.interfaces.INewsletter.providedBy(candidate):
            return candidate
        else:
            candidate = getattr(candidate, '__parent__', None)


@glob(zope.interface.Interface)
def newsletter(context):
    return get_newsletter(context) is not None


@glob(zope.interface.Interface)
def middle_ad_position(context):
    newsletter = get_newsletter(context)
    if newsletter is None:
        return
    # Newsletter is connected to category only through containment in
    # repository, so we need to map working copies to repository objects.
    newsletter = zeit.cms.interfaces.ICMSContent(newsletter.uniqueId)
    category = zeit.newsletter.interfaces.INewsletterCategory(
        newsletter, None)
    if category is None:
        return
    return category.ad_middle_groups_above + 1


@glob(zope.interface.Interface)
def last_position(context):
    return len(context.__parent__)
