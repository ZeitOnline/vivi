from zeit.content.cp.i18n import MessageFactory as _
import zc.iso8601.parse
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.interface
import lxml.objectify


# XXX too much duplication between VideoBlock and AudioBlock.
# wants to be refactored, probably factory-style like cpextra.py

class AVBlock(zeit.content.cp.blocks.block.Block):

    @property
    def first_child(self):
        return self.xml.getchildren()[0]

    @property
    def format(self):
        return self.first_child.get('format')

    @format.setter
    def format(self, value):
        self._p_changed = True
        return self.first_child.set('format', value)

    # XXX very abridged version of zeit.cms.content.dav.DatetimeProperty
    @property
    def expires(self):
        value = self.first_child.get('expires')
        if value:
            return zc.iso8601.parse.datetimetz(value)

    @expires.setter
    def expires(self, value):
        self._p_changed = True
        value = value.isoformat() if value else ''
        self.xml.getchildren()[0].set('expires', value)


class VideoBlock(AVBlock):

    zope.interface.implements(zeit.content.cp.interfaces.IVideoBlock)

    id = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.video', 'videoID')
    player = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.video', 'player')

    media_type = 'video'

    def __init__(self, context, xml):
        super(VideoBlock, self).__init__(context, xml)
        if len(self.xml.getchildren()) == 0:
            self.xml.append(lxml.objectify.E.video())


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'video', _('Videoblock'))


class AudioBlock(AVBlock):

    zope.interface.implements(zeit.content.cp.interfaces.IAVBlock)

    id = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.audio', 'audioID')

    media_type = 'audio'

    def __init__(self, context, xml):
        super(AudioBlock, self).__init__(context, xml)
        if len(self.xml.getchildren()) == 0:
            self.xml.append(lxml.objectify.E.audio())


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'audio', _('Audioblock'))
