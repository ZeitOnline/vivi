import zeit.cms.browser.view
import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces
import zope.formlib.form


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IHeaderImageBlock).omit(
            *list(zeit.content.cp.interfaces.IBlock))


class Display(zeit.cms.browser.view.Base):

    @property
    def image_url(self):
        if not self.context.image:
            return None
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.cp')
        return '%s%s/@@raw' % (
            self.url(repository), self.context.image.variant_url(
                config['header-image-variant'], thumbnail=True))
