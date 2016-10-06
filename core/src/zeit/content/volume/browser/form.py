from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import transaction
import zeit.cms.browser.form
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.settings.interfaces
import zeit.content.image.interfaces
import zeit.content.volume.interfaces
import zeit.content.volume.volume
import zope.component
import zope.formlib.form
import zope.formlib.interfaces
import zope.interface
import zope.schema


class DuplicateVolumeWarning(Exception):

    zope.interface.implements(zope.formlib.interfaces.IWidgetInputError)

    def doc(self):
        return _(u'A volume with the given name already exists.')


class Base(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.volume.interfaces.IVolume).select(
            'product', 'year', 'volume',
            'date_digital_published', 'teaserText')

    field_groups = (
        gocept.form.grouped.Fields(
            _('Volume'),
            ('product', 'year', 'volume',
             'date_digital_published', 'teaserText'),
            css_class='column-left'),
        gocept.form.grouped.RemainingFields(
            _('Texts'),
            css_class='column-right'),
    )

    def __init__(self, context, request):
        """Dynamically add fields for `IImageGroup` references from XML config.

        We want to define the available references via an XML source, thus we
        must read them on the fly and generate the schema fields accordingly.

        To store the chosen values, we set `interface` on the field, thus it is
        adapted to `IVolumeCovers` which stores the information in the the XML
        of `Volume`.

        """
        super(Base, self).__init__(context, request)
        source = zeit.content.volume.interfaces.VOLUME_COVER_SOURCE(
            self.context)
        for name in source:
            field = zope.schema.Choice(
                title=source.title(name), required=False,
                source=zeit.content.image.interfaces.imageGroupSource)
            field.__name__ = name
            field.interface = zeit.content.volume.interfaces.IVolumeCovers
            self.form_fields += zope.formlib.form.FormFields(field)

        self.field_groups += (gocept.form.grouped.Fields(
            _('Covers'), tuple(source), css_class='column-right'),)


class Add(Base, zeit.cms.browser.form.AddForm):

    title = _('Add volume')
    factory = zeit.content.volume.volume.Volume
    checkout = False

    def suggestName(self, object):
        """Define __name__ automatically."""
        return str(object.volume).rjust(2, '0')

    def setUpWidgets(self, *args, **kw):
        super(Add, self).setUpWidgets(*args, **kw)
        settings = zeit.cms.settings.interfaces.IGlobalSettings(self.context)
        if not self.widgets['year'].hasInput():
            self.widgets['year'].setRenderedValue(settings.default_year)
        if not self.widgets['volume'].hasInput():
            self.widgets['volume'].setRenderedValue(settings.default_volume)

    def add(self, object):
        path = self.volume_location(object)
        # The last part of the path is the filename for the volume object.
        volume_filename = path[-1]
        container = zeit.cms.content.add.find_or_create_folder(*path[:-1])
        if self._check_duplicate_volume(container, volume_filename):
            return
        container[volume_filename] = object
        self._created_object = container[volume_filename]
        self._finished_add = True

    def volume_location(self, object):
        location = object.product.location.format(
            year=object.year, name=str(object.volume).rjust(2, '0'))
        location = location.replace(zeit.cms.interfaces.ID_NAMESPACE, '')
        return [x for x in location.split('/') if x]

    def _check_duplicate_volume(self, location, name):
        if location.get(name) is not None:
            transaction.doom()
            self.errors = (DuplicateVolumeWarning(),)
            self.status = _('There were errors')
            self.form_reset = False
            return True
        return False


class Edit(Base, zeit.cms.browser.form.EditForm):

    title = _('Edit volume')


class Display(Base, zeit.cms.browser.form.DisplayForm):

    title = _('View volume')
