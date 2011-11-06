# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.brightcove.interfaces import DAV_NAMESPACE
from zeit.cms.content.dav import DAVProperty
from zeit.cms.i18n import MessageFactory as _
import zeit.content.video.video
import zope.schema


zeit.content.video.video.Video.brightcove_id = DAVProperty(
    zope.schema.ASCIILine(
        title=_('Brightcove Id'),
        readonly=True,
        ),
    DAV_NAMESPACE,
    'id',
    )
