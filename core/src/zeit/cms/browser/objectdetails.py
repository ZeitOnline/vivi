# coding: utf8
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zope.annotation.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.dublincore.interfaces
import zope.interface


@zope.interface.implementer(zope.annotation.interfaces.IAttributeAnnotatable)
class NoMetadata(zeit.cms.content.metadata.CommonMetadata):
    default_template = '<empty/>'


NO_METADATA = NoMetadata()


class Details(zeit.cms.browser.view.Base):
    """Render details about an content object."""

    @zope.cachedescriptors.property.Lazy
    def list_repr(self):
        return zope.component.queryMultiAdapter(
            (self.context, self.request), zeit.cms.browser.interfaces.IListRepresentation
        )

    @zope.cachedescriptors.property.Lazy
    def common_metadata(self):
        return zeit.cms.content.interfaces.ICommonMetadata(self.context, NO_METADATA)

    @property
    def teaser_title(self):
        if self.common_metadata is not NO_METADATA:
            return self.common_metadata.teaserTitle
        if self.list_repr is not None:
            return self.list_repr.title
        return None

    @property
    def teaser_text(self):
        if self.common_metadata is not NO_METADATA:
            return self.common_metadata.teaserText
        return None

    @property
    def preview_url(self):
        return zope.component.queryMultiAdapter(
            (self.context, 'preview'), zeit.cms.browser.interfaces.IPreviewURL
        )

    @property
    def live_url(self):
        return zope.component.queryMultiAdapter(
            (self.context, 'live'), zeit.cms.browser.interfaces.IPreviewURL
        )

    @property
    def resources_filename(self):
        urlstring = zope.component.queryMultiAdapter(
            (self.context, 'live'), zeit.cms.browser.interfaces.IPreviewURL
        )
        return urlstring.split('/')[-1]

    @zope.cachedescriptors.property.Lazy
    def graphical_preview_url(self):
        thumbnail = zope.component.queryMultiAdapter((self.context, self.request), name='thumbnail')
        if thumbnail is None:
            return None
        return self.url('@@thumbnail')

    @zope.cachedescriptors.property.Lazy
    def large_graphical_preview_url(self):
        thumbnail = zope.component.queryMultiAdapter(
            (self.context, self.request), name='thumbnail_large'
        )
        if thumbnail is None:
            return None
        return self.url('@@thumbnail_large')

    @property
    def author(self):
        if self.common_metadata is NO_METADATA:
            return None
        if self.common_metadata.authorships:
            author = self.common_metadata.authorships[0].target
            if author is not None:
                return author.display_name
        elif self.common_metadata.authors:
            return self.common_metadata.authors[0]
        return None

    @property
    def volume(self):
        year = self.common_metadata.year
        vol = self.common_metadata.volume
        if year is None:
            return None
        return (vol and '%s/%s' % (vol, year)) or '%s' % (year)

    @property
    def display_metadata(self):
        lsc = zeit.cms.content.interfaces.ISemanticChange(self.context).last_semantic_change
        entries = {
            'teaser_title': self.teaser_title,
            'created': lsc and lsc.strftime('%d.%m.%Y'),
            'ressort': self.common_metadata.ressort,
            'author': self.author,
            'volume': self.volume,
        }
        sorted_entries = []
        for key in ['teaser_title', 'created', 'ressort', 'author', 'volume']:
            if entries[key]:
                sorted_entries.append([key, entries[key]])
        return sorted_entries

    def display_metadata_short(self):
        lsc = zeit.cms.content.interfaces.ISemanticChange(self.context).last_semantic_change
        return [
            x
            for x in [
                lsc and lsc.strftime('%d.%m.%Y'),
                self.common_metadata.ressort,
                self.author,
                self.volume,
            ]
            if x
        ]

    @property
    def type_declaration(self):
        no_type = type('NoTypeDeclaration', (object,), {'type_identifier': 'unknown'})
        return zeit.cms.interfaces.ITypeDeclaration(self.context, no_type)
