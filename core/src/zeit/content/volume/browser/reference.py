import zope.component
import zope.formlib.form
import zope.formlib.interfaces

import zeit.cms.browser.objectdetails
import zeit.cms.browser.view
import zeit.cms.repository.interfaces
import zeit.content.volume.interfaces
import zeit.edit.browser.form


class EditReference(zeit.edit.browser.form.InlineForm):
    """Display the additional field `volume_note` for references."""

    legend = ''

    form_fields = zope.formlib.form.FormFields(
        zeit.content.volume.interfaces.IVolumeReference,
        # support read-only mode, see
        # zeit.content.article.edit.browser.form.FormFields
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE,
    ).select('volume_note')

    @property
    def prefix(self):
        return 'reference-details-%s' % self.context.target.uniqueId


class ReferenceDetailsHeading(zeit.cms.browser.objectdetails.Details):
    """Overwrite __init__ to work on `context.target`."""

    def __init__(self, context, request):
        super().__init__(context.target, request)


class Display(zeit.cms.browser.view.Base):
    def description(self):
        volume = self.context.target
        return '{}, Jahrgang: {}, Ausgabe {}'.format(
            volume.product.title,
            volume.year,
            volume.volume,
        )

    def cover_image(self):
        height = 300

        if not self.context.target:
            return ''

        # Right now the first definition in VolumeCoverSource is taken
        # the cover for the reference. That's at least nontransparent to
        # someone who edits the volume-covers.xml. Maybe make it
        # configurable via the source?
        source = zeit.content.volume.interfaces.VOLUME_COVER_SOURCE(self.context.target)
        cover_name = list(source)[0]
        cover = self.context.target.get_cover(cover_name, self.context.target.product.id)
        if not cover:
            return ''
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        cover_url = '{}{}/@@raw'.format(
            self.url(repository), cover.variant_url('original', thumbnail=True)
        )
        return '<img src="{}" alt="" height="{}" border="0" />'.format(cover_url, height)
