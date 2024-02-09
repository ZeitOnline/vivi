import collections

import zc.sourcefactory.basic
import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _


class EntityTypeSource(zc.sourcefactory.basic.BasicSourceFactory):
    # XXX Keep in sync with tagger-generated whitelist.xml
    values = collections.OrderedDict(
        [
            ('free', _('entity-type-free')),
            ('Organization', _('entity-type-organization')),
            ('Location', _('entity-type-location')),
            ('Person', _('entity-type-person')),
        ]
    )

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values[value]


class ISEO(zope.interface.Interface):
    html_title = zope.schema.TextLine(title=_('HTML title'), required=False)

    html_description = zope.schema.Text(title=_('HTML description'), required=False)

    meta_robots = zope.schema.Text(title=_('Meta robots'), required=False)

    hide_timestamp = zope.schema.Bool(title=_('Hide timestamp'), required=False)

    disable_intext_links = zope.schema.Bool(title=_('Disable intext links'), required=False)

    disable_enrich = zope.schema.Bool(title=_('Disable enrich'), required=False)

    keyword_entity_type = zope.schema.Choice(
        title=_('Keyword entity type'), source=EntityTypeSource(), required=False
    )
