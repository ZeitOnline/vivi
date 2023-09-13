from zeit.cms.i18n import MessageFactory as _
import zope.interface
import zope.schema
import zeit.cms.content.interfaces
import zeit.cms.content.contentsource


class IAudio(zeit.cms.content.interfaces.IXMLContent):
    title = zope.schema.TextLine(title=_("Title"), required=False)
    serie = zope.schema.TextLine(title=_("Serie"), required=False)
    image = zope.schema.URI(title=_('Remote image URL'), required=False)
    episode_id = zope.schema.TextLine(title=_("Episode Id"))
    url = zope.schema.URI(title=_("Url"), required=False)
    duration = zope.schema.Int(title=_("Duration"), required=False)


class AudioSource(zeit.cms.content.contentsource.CMSContentSource):
    name = 'audio'
    check_interfaces = (IAudio,)


class IAudios(zope.interface.Interface):
    items = zope.schema.Tuple(
        title=_("Audios"),
        value_type=zope.schema.Choice(source=AudioSource()))
