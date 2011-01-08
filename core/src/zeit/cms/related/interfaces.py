# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface
import zope.schema

import zeit.cms.content.contentsource

from zeit.cms.i18n import MessageFactory as _


class IRelatedContent(zope.interface.Interface):
    """Relate other content."""

    related = zope.schema.Tuple(
        title=_("Related content"),
        description=_("Objects that are related to this object."),
        default=(),
        required=False,
        value_type=zope.schema.Choice(
            source=zeit.cms.content.contentsource.cmsContentSource))
