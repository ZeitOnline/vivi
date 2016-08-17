from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.cms.settings.interfaces
import zeit.content.volume.interfaces
import zeit.content.volume.volume
import zope.formlib.form


class Base(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.volume.interfaces.IVolume).select(
            'product', 'year', 'volume', 'teaserText')

    field_groups = (
        gocept.form.grouped.Fields(
            _('Volume'),
            ('product', 'year', 'volume', 'teaserText'),
            css_class='column-left'),
        gocept.form.grouped.RemainingFields(
            _('Texts'),
            css_class='column-right'),
    )


class Add(Base, zeit.cms.browser.form.AddForm):

    title = _('Add volume')
    factory = zeit.content.volume.volume.Volume
    checkout = False

    def suggestName(self, object):
        """Define __name__ automatically using year / volume."""
        return 'ausgabe-{year}-{volume}'.format(
            year=object.year, volume=str(object.volume).rjust(2, '0'))

    def setUpWidgets(self, *args, **kw):
        super(Add, self).setUpWidgets(*args, **kw)
        settings = zeit.cms.settings.interfaces.IGlobalSettings(self.context)
        if not self.widgets['year'].hasInput():
            self.widgets['year'].setRenderedValue(settings.default_year)
        if not self.widgets['volume'].hasInput():
            self.widgets['volume'].setRenderedValue(settings.default_volume)


class Edit(Base, zeit.cms.browser.form.EditForm):

    title = _('Edit volume')


class Display(Base, zeit.cms.browser.form.DisplayForm):

    title = _('View volume')
