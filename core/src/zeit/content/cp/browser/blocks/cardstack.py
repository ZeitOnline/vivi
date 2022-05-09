import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces
import zope.formlib.form
import zope.formlib.source
import zope.formlib.widget


class ColorSourceWidget(zope.formlib.source.SourceDropdownWidget):

    """
    A color picker which expects hex values as the underlying source
    """

    cssClass = 'color-source-widget'

    # adjust SourceDropdownWidgets to make it work as custom_widget...
    def __init__(self, field, request):
        super().__init__(field, field.source, request)

    @property
    def size(self):
        return len(self.context.source)

    def renderItem(self, index, text, value, name, cssClass):
        return self._render_element(value, text)

    def renderSelectedItem(self, index, text, value, name, cssClass):
        return self._render_element(value, text, selected='selected')

    def _render_element(self, value, color_code, **kw):
        return zope.formlib.widget.renderElement(
            'option', contents=color_code,
            value=value,
            cssClass=self.cssClass,
            style="background-color: %s" % color_code,
            **kw)


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.ICardstackBlock).select(
        'card_id',
        'is_advertorial',
        'cardstack_background_color')

    form_fields['cardstack_background_color'].custom_widget = ColorSourceWidget
