# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import datetime
import rwproperty
import time
import zc.iso8601.parse
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.interface


class AVBlock(zeit.content.cp.blocks.block.Block):

    media_type = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'module')
    format = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'format')

    # XXX very abridged version of zeit.cms.content.dav.DatetimeProperty
    @rwproperty.getproperty
    def expires(self):
        value = self.xml.get('expires')
        if value is None:
            return None
        else:
            return zc.iso8601.parse.datetimetz(value)

    @rwproperty.setproperty
    def expires(self, value):
        self.xml.set('expires', value.isoformat())


class VideoBlock(AVBlock):

    zope.interface.implements(zeit.content.cp.interfaces.IAVBlock)

    id = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'videoID')

    def __init__(self, context, xml):
        super(VideoBlock, self).__init__(context, xml)
        self.media_type = 'video'


VideoBlockFactory = zeit.content.cp.blocks.block.blockFactoryFactory(
    zeit.content.cp.interfaces.IRegion,
    VideoBlock, 'videoblock', _('Videoblock'))


class AudioBlock(AVBlock):

    zope.interface.implements(zeit.content.cp.interfaces.IAVBlock)

    id = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'audioID')

    def __init__(self, context, xml):
        super(AudioBlock, self).__init__(context, xml)
        self.media_type = 'audio'


AudioBlockFactory = zeit.content.cp.blocks.block.blockFactoryFactory(
    zeit.content.cp.interfaces.IRegion,
    AudioBlock, 'audioblock', _('Audioblock'))
