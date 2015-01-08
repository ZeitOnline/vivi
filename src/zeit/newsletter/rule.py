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


@glob(zope.interface.Interface)
def newsletter(context):
    return zeit.newsletter.interfaces.INewsletter(context, None) is not None


@glob(zope.interface.Interface)
def middle_ad_position(context):
    newsletter = zeit.newsletter.interfaces.INewsletter(context, None)
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
def thisweeks_ad_position(context):
    newsletter = zeit.newsletter.interfaces.INewsletter(context, None)
    if newsletter is None:
        return
    # Newsletter is connected to category only through containment in
    # repository, so we need to map working copies to repository objects.
    newsletter = zeit.cms.interfaces.ICMSContent(newsletter.uniqueId)
    category = zeit.newsletter.interfaces.INewsletterCategory(
        newsletter, None)
    if category is None:
        return
    return category.ad_thisweeks_groups_above + 1


@glob(zope.interface.Interface)
def last_position(context):
    return len(context.__parent__)
