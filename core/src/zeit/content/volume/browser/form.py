from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.content.volume.interfaces
import zeit.content.volume.volume
import zope.formlib.form


class Base(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.volume.interfaces.IVolume).select(
            'year', 'volume', 'teaserText')

    field_groups = (
        gocept.form.grouped.Fields(
            _('Volume'),
            ('year', 'volume', 'teaserText'),
            css_class='column-left'),
        gocept.form.grouped.RemainingFields(
            _('Texts'),
            css_class='column-right'),
    )


class Add(Base, zeit.cms.browser.form.AddForm):

    title = _('Add volume')
    factory = zeit.content.volume.volume.Volume

    def create(self, data):
        """Define __name__ automatically using year / volume."""
        volume = super(Add, self).create(data)
        volume.__name__ = 'ausgabe-{year}-{volume}'.format(
            year=data['year'], volume=str(data['volume']).rjust(2, '0'))
        return volume


class Edit(Base, zeit.cms.browser.form.EditForm):

    title = _('Edit volume')


class Display(Base, zeit.cms.browser.form.DisplayForm):

    title = _('View volume')
