from urllib.parse import urlparse
import os.path

import zope.interface
import zope.schema

from zeit.cms.admin.interfaces import IAdjustSemanticPublish
from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.redirect.interfaces import IRenameInfo
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.image.interfaces import IImages
from zeit.content.link.link import Link
import zeit.cms.browser.menu


class ISchema(zope.interface.Interface):
    target = zope.schema.TextLine(
        title=_('Redirect path'), constraint=zeit.cms.repository.browser.move.valid_name
    )


class Redirect(zeit.cms.browser.lightbox.Form):
    form_fields = zope.formlib.form.FormFields(ISchema)

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile('redirect.pt')

    def get_data(self):
        target = self.context.uniqueId
        for id in reversed(IRenameInfo(self.context).previous_uniqueIds):
            # XXX IAutomaticallyRenameable doesn't really define this; see
            # z.c.article.browser.form.AddAndCheckout
            if not id.endswith('.tmp'):
                target = id
                break
        return {'target': urlparse(target).path}

    @zope.formlib.form.action(_('Create redirect'))
    def link(self, action, data):
        path = os.path.dirname(data['target'])
        name = os.path.basename(data['target'])
        container = zeit.cms.interfaces.ICMSContent(zeit.cms.interfaces.ID_NAMESPACE + path[1:])
        container[name] = Link()
        link = container[name]

        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        with checked_out(link, temporary=False) as target:
            self.copy_values(self.context, target)
            target.url = self.context.uniqueId.replace(
                zeit.cms.interfaces.ID_NAMESPACE, config['live-prefix']
            )
        self.adjust_workflow(self.context, link)
        self.context = link  # also sets nextURL

    def copy_values(self, source, target):
        for iface in [ICommonMetadata, IImages]:
            src = iface(source)
            tgt = iface(target)
            for field in zope.schema.getFields(iface).values():
                __traceback_info__ = (field,)
                if field.readonly:
                    continue
                value = field.get(src)
                if value != field.missing_value and value != field.default:
                    field.set(tgt, value)

    def adjust_workflow(self, source, target):
        source_pub = IPublishInfo(source)
        target_pub = IAdjustSemanticPublish(target)
        target_pub.adjust_first_released = source_pub.date_first_released
        target_pub.adjust_semantic_publish = source_pub.date_last_published_semantic
        IPublishInfo(target).urgent = True


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):
    title = _('Create redirect')
