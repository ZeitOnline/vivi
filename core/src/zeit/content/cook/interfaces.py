from zeit.cms.i18n import MessageFactory as _
import collections
import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zeit.content.article.interfaces
import zeit.content.video.interfaces
import zope.schema

import zeit.content.author.interfaces


class DisplayModeSource(zeit.cms.content.sources.SimpleFixedValueSource):

    values = collections.OrderedDict([
        ("images", _("use images")),
        ("video", _("use video")),
    ])


class ICook(
    zeit.content.author.interfaces.IAuthor
):
    pass
