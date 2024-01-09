import zope.formlib.form

import zeit.content.cp.browser.blocks.teaser


class EditCommon(zeit.content.cp.browser.blocks.teaser.EditCommon):
    form_fields = zope.formlib.form.FormFields(zeit.content.cp.interfaces.ILocalTeaserBlock).select(
        'references',
        'teaserSupertitle',
        'teaserTitle',
        'teaserText',
        'image',
        'fill_color',
        'force_mobile_image',
    )
