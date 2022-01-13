import zeit.content.cp.browser.blocks.teaser
import zope.formlib.form


class EditCommon(zeit.content.cp.browser.blocks.teaser.EditCommon):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.ILocalTeaserBlock).select(
            'teaserSupertitle', 'teaserTitle', 'teaserText',
            'image', 'fill_color',
            'visible_mobile', 'force_mobile_image')
