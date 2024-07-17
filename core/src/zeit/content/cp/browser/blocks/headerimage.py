import zope.formlib.form

import zeit.cms.browser.view
import zeit.cms.config
import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):
    form_fields = zope.formlib.form.Fields(zeit.content.cp.interfaces.IHeaderImageBlock).omit(
        *list(zeit.content.cp.interfaces.IBlock)
    )


class Display(zeit.cms.browser.view.Base):
    @property
    def image_url(self):
        if not self.context.image:
            return None
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        return '%s%s/@@raw' % (
            self.url(repository),
            self.context.image.variant_url(
                zeit.cms.config.required('zeit.content.cp', 'header-image-variant'), thumbnail=True
            ),
        )
