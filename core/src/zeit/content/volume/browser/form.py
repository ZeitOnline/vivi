from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import grokcore.component as grok
import transaction
import zeit.cms.browser.form
import zeit.cms.interfaces
import zeit.cms.settings.interfaces
import zeit.content.image.interfaces
import zeit.content.volume.interfaces
import zeit.content.volume.volume
import zope.formlib.form
import zope.formlib.interfaces
import zope.interface
import zope.schema


@zope.interface.implementer(zope.formlib.interfaces.IWidgetInputError)
class DuplicateVolumeWarning(Exception):

    def doc(self):
        return _('A volume with the given name already exists.')


class Base:

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
    )

    def __init__(self, context, request):
        """Dynamically add fields for `IImageGroup` references from XML config.

        We want to define the available references via an XML source, thus we
        must read them on the fly and generate the schema fields accordingly.

        To store the chosen values, we set `interface` on the field, thus it is
        adapted to `IVolumeCovers` which stores the information in the the XML
        of `Volume`.

        """
        super().__init__(context, request)
        covers = zeit.content.volume.interfaces.VOLUME_COVER_SOURCE(
            self.context)
        # In the Addform there is no volume object. Thus we have to wait for
        # it to be created.
        if getattr(self.context, 'product', None) is not None:
            for product in (
                    [self.context.product] +
                    self.context.product.dependent_products):
                fieldnames = []
                for name in covers:
                    field = zope.schema.Choice(
                        title=covers.title(name), required=False,
                        source=zeit.content.image.interfaces.imageGroupSource)
                    field.__name__ = 'cover_%s_%s' % (product.id, name)
                    field.interface = ICovers
                    self.form_fields += zope.formlib.form.FormFields(field)
                    fieldnames.append(field.__name__)
                self.field_groups += (gocept.form.grouped.Fields(
                    product.title, fieldnames, css_class='column-right'),)


class Add(Base, zeit.cms.browser.form.AddForm):

    title = _('Add volume')
    factory = zeit.content.volume.volume.Volume

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        settings = zeit.cms.settings.interfaces.IGlobalSettings(self.context)
        if not self.widgets['year'].hasInput():
            self.widgets['year'].setRenderedValue(settings.default_year)
        if not self.widgets['volume'].hasInput():
            self.widgets['volume'].setRenderedValue(settings.default_volume)

    def add(self, volume):
        folder, filename = self._create_folder(volume, volume.product.location)
        if folder is None:
            return
        folder[filename] = volume

        # XXX copy&paste from superclass
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(
            folder[filename], None)
        if manager is not None and manager.canCheckout:
            self._created_object = manager.checkout()
            self._checked_out = True

        cp_template = zeit.cms.interfaces.ICMSContent(
            volume.product.cp_template, None)
        if zeit.content.text.interfaces.IPythonScript.providedBy(cp_template):
            folder, filename = self._create_folder(
                volume, volume.product.centerpage)
            if folder is None:
                return
            folder[filename] = cp_template(volume=volume)

        self._finished_add = True

    def _create_folder(self, volume, location_template):
        path, filename = self._make_path(volume, location_template)
        folder = zeit.cms.content.add.find_or_create_folder(*path)
        if self._check_duplicate_item(folder, filename):
            return (None, None)
        return folder, filename

    def _make_path(self, volume, location_template):
        uniqueId = volume.fill_template(location_template)
        uniqueId = uniqueId.replace(zeit.cms.interfaces.ID_NAMESPACE, '')
        path = [x for x in uniqueId.split('/') if x]
        return path[:-1], path[-1]

    def _check_duplicate_item(self, folder, name):
        if name in folder:
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


class ICovers(zope.interface.Interface):
    """
    This interface is used to define the available covers via an Cover XML
    source for all Products to store the chosen cover images as references
    on the IVolume. It is only needed for the interaction with the formlib.
    """


@grok.implementer(ICovers)
class Covers(grok.Adapter):

    grok.context(zeit.content.volume.interfaces.IVolume)

    def __getattr__(self, name):
        if not name.startswith('cover_'):
            return super().__getattr__(name)
        name = name.replace('cover_', '', 1)
        product, cover = name.split('_')
        # We dont want the fallback in the UI
        return self.context.get_cover(cover, product, use_fallback=False)

    def __setattr__(self, name, value):
        if not name.startswith('cover_'):
            super().__setattr__(name, value)
            return
        name = name.replace('cover_', '', 1)
        product, cover = name.split('_')
        self.context.set_cover(cover, product, value)
