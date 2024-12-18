import grokcore.component as grok
import pendulum
import zope.component

from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import ITickarooLiveblog
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.modules.interfaces
import zeit.content.modules.liveblog


@grok.implementer(zeit.content.article.edit.interfaces.ILiveblog)
class Liveblog(zeit.content.article.edit.block.Block):
    type = 'liveblog'

    blog_id = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'blogID', zeit.content.article.edit.interfaces.ILiveblog['blog_id']
    )
    _version = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'version', zeit.content.article.edit.interfaces.ILiveblog['version'], use_default=True
    )
    collapse_preceding_content = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.',
        'collapse-preceding-content',
        zeit.content.article.edit.interfaces.ILiveblog['collapse_preceding_content'],
        use_default=True,
    )

    # BBB
    show_timeline_in_teaser = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.',
        'show-timeline-in-teaser',
        zeit.content.article.edit.interfaces.ILiveblog['show_timeline_in_teaser'],
        use_default=True,
    )

    timeline_template = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.',
        'timeline_template',
        zeit.content.article.edit.interfaces.ILiveblog['timeline_template'],
    )

    LIVEBLOG_VERSION_UPDATE = pendulum.datetime(2018, 8, 6)

    @property
    def version(self):
        # XXX Cannot use the version property, since we had `use_default=True`
        # since 3.38.5, and thus we have old articles without a version in XML
        # that mean "2", and newer with the same XML that mean "3". Sigh.
        version = self.xml.get('version')
        if version:
            return version

        article = zeit.content.article.interfaces.IArticle(self)
        dfr = zeit.cms.workflow.interfaces.IPublishInfo(article).date_first_released
        if not dfr:
            return '3'
        elif dfr > self.LIVEBLOG_VERSION_UPDATE:
            return '3'
        else:
            return '2'

    @version.setter
    def version(self, value):
        self._version = value


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = Liveblog
    title = _('Liveblog')


@grok.subscribe(
    zeit.content.article.interfaces.IArticle, zeit.cms.checkout.interfaces.IAfterCheckoutEvent
)
def set_lsc_default_for_liveblogs(context, event):
    if event.publishing:
        return
    for block in context.body.values():
        if zeit.content.article.edit.interfaces.ILiveblog.providedBy(block):
            zeit.cms.content.interfaces.ISemanticChange(context).has_semantic_change = True
            break


@grok.implementer(zeit.content.article.edit.interfaces.ITickarooLiveblog)
class TickarooLiveblog(
    zeit.content.article.edit.block.Block, zeit.content.modules.liveblog.TickarooLiveblog
):
    type = 'tickaroo_liveblog'


@zope.component.adapter(ITickarooLiveblog)
class TickarooLiveblogFactory(zeit.content.article.edit.block.BlockFactory):
    produces = TickarooLiveblog
    title = _('Tickaroo liveblog block')
