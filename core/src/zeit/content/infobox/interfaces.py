# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zc.form.field
import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zope.interface
import zope.schema


class IInfobox(zeit.cms.content.interfaces.IXMLContent):

    supertitle = zope.schema.TextLine(title=_('Supertitle'))

    contents = zope.schema.Tuple(
        title=_('Contents'),
        value_type=zc.form.field.Combination(
            (zope.schema.TextLine(
                title=_('Title')),
              zc.form.field.HTMLSnippet(title=_("Text")),
            )))



class InfoboxSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'zeit.content.infobox'
    check_interfaces = (IInfobox,)


infoboxSource = InfoboxSource()


class IInfoboxReference(zope.interface.Interface):

    infobox = zope.schema.Choice(
        title=_('Infobox'),
        required=False,
        source=infoboxSource)
