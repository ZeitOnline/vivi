# Copyright (c) 2014 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.edit.rule import glob
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
    candidate = context
    while not zeit.newsletter.interfaces.INewsletter.providedBy(candidate):
        candidate = getattr(candidate, '__parent__', None)
        if candidate is None:
            return False
    else:
        return True


@glob(zope.interface.Interface)
def last_position(context):
    return len(context.__parent__)
