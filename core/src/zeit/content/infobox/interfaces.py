import zc.form.field
import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.contentsource
import zeit.cms.content.interfaces


class IInfobox(
    zeit.cms.content.interfaces.IXMLContent,
    zeit.cms.content.interfaces.ICommonMetadata,
    zeit.cms.content.interfaces.ISkipDefaultChannel,
):
    supertitle = zope.schema.TextLine(title=_('Supertitle'))

    # BBB I don't think more than one entry is currently used
    contents = zope.schema.Tuple(
        title=_('Contents'),
        value_type=zc.form.field.Combination(
            (zope.schema.TextLine(title=_('Title')), zc.form.field.HTMLSnippet(title=_('Text')))
        ),
    )

    ressort = zeit.cms.content.interfaces.ICommonMetadata['ressort'].bind(object())
    ressort.context = None
    ressort.required = False


class InfoboxSource(zeit.cms.content.contentsource.CMSContentSource):
    name = 'zeit.content.infobox'
    check_interfaces = (IInfobox,)


infoboxSource = InfoboxSource()


class IInfoboxReference(zope.interface.Interface):
    infobox = zope.schema.Choice(title=_('Infobox'), required=False, source=infoboxSource)


class IDebate(zope.interface.Interface):
    action_url = zope.schema.TextLine(
        title=_('Debate action URL'), description=_('debate-action-url-description'), required=False
    )
