from collections import defaultdict, namedtuple
import grokcore.component
import json
import urlparse
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zope.app.appsetup.appsetup
import zope.app.pagetemplate
import zope.component.hooks
import zope.formlib.itemswidgets
import zope.formlib.source
import zope.formlib.widget
import zope.lifecycleevent
import zope.schema.interfaces


class Widget(grokcore.component.MultiAdapter,
             zope.formlib.widget.SimpleInputWidget,
             zeit.cms.browser.view.Base):
    """Widget to edit tags on context.

    - "Update" link uses an tagging mechanism to add tags to content
    - The user can sort and (de-)activate tags, but not manually add them.

    """

    grokcore.component.adapts(
        zope.schema.interfaces.ITuple,
        zeit.cms.tagging.source.IWhitelistSource,
        zeit.cms.browser.interfaces.ICMSLayer)
    grokcore.component.provides(
        zope.formlib.interfaces.IInputWidget)

    template = zope.app.pagetemplate.ViewPageTemplateFile('widget.pt')

    def __init__(self, context, source, request):
        super(Widget, self).__init__(context, request)
        self.source = source

    def __call__(self):
        return self.template()

    @property
    def autocomplete_source_url(self):
        return self.url(
            zope.component.hooks.getSite(), '@@zeit.cms.tagging.search')

    @property
    def display_update_button(self):
        renameable = zeit.cms.repository.interfaces.IAutomaticallyRenameable(
            self.context.context)
        return (self.context.queryTaggedValue(
            'zeit.cms.tagging.updateable') and not renameable.renameable)

    def _toFormValue(self, value):
        # Re #12478: When iterating over keywords, fall back to an empty
        # sequence since the value None may occur in spite of the schema
        # either requiring at least one keyword or specifying a default of ().
        # An example of this is when checking out existing content that
        # doesn't have any keywords.
        # XXX Maybe there's a better place to fix this inconsistency but right
        # now I opt for a quick solution to a fair mess of failing tests.
        return json.dumps([{
            'code': x.uniqueId,
            'label': x.label,
            'pinned': x.pinned} for x in value or ()])

    def _toFieldValue(self, value):
        tags = json.loads(value)
        result = []
        for item in tags:
            tag = zeit.cms.interfaces.ICMSContent(item['code'])
            tag.pinned = item['pinned']
            result.append(tag)
        return tuple(result)

    def display_tms_link(self):
        return self.tms_host and self.request.interaction.checkPermission(
            'zeit.cms.tagging.ViewInTMS', self.context)

    @property
    def tms_host(self):
        try:
            # XXX This dependency is the wrong way around, but creating
            # an abstraction instead doesn't really seem worthwile either.
            import zeit.retresco.interfaces
            tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
            return urlparse.urlparse(tms.url).netloc
        except (ImportError, LookupError):
            return None

    @property
    def uuid(self):
        return zeit.cms.content.interfaces.IUUID(self.context.context).id


class UpdateTags(zeit.cms.browser.view.JSON):

    def json(self):
        tagger = zeit.cms.tagging.interfaces.ITagger(self.context)
        tagger.update()
        zope.lifecycleevent.modified(self.context)
        return dict(tags=[
            dict(code=tag.uniqueId,
                 label=tag.label,
                 pinned=tag.pinned)
            for tag in tagger.values()])


class TagsWithTopicpages(zeit.cms.browser.view.JSON):

    def json(self):
        # don't want to add this dependency to zeit.cms
        keywords_with_link = get_tags_with_topicpages(self.context)
        return keywords_with_link

class DisplayWidget(grokcore.component.MultiAdapter,
                    zope.formlib.itemswidgets.ListDisplayWidget):

    grokcore.component.adapts(
        zope.schema.interfaces.ITuple,
        zeit.cms.tagging.source.IWhitelistSource,
        zeit.cms.browser.interfaces.ICMSLayer)
    grokcore.component.provides(
        zope.formlib.interfaces.IDisplayWidget)

    template = zope.app.pagetemplate.ViewPageTemplateFile('display-tag.pt')
    tag_highling_css_class = 'with-topic-page'

    def __init__(self, field, source, request):
        super(DisplayWidget, self).__init__(
            field,
            zope.formlib.source.IterableSourceVocabulary(source, request),
            request)
        self.tags_with_topicpages = defaultdict(
            str, get_tags_with_topicpages(self.context.context))

    def __call__(self):
        return self.template()

    def _text(self, item):
        return self.textForValue(self.vocabulary.getTerm(item))

    def items(self):
        items = []
        Tag = namedtuple('Tag', ['text', 'link', 'css_class'])
        for item in self._getFormValue():
            text = self._text(item)
            link = self.tags_with_topicpages[item.uniqueId]
            css_class = self.tag_highling_css_class if link else ''
            items.append(Tag(text, link, css_class))
        return items


def get_tags_with_topicpages(article):
    import zeit.retresco.interfaces
    tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
    config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
    live_prefix = config.get('live_prefix', 'https://www.zeit.de/')
    keywords_with_link = tms.get_article_keywords(
        article,
        published=False)
    return {tag.uniqueId: live_prefix + tag.link
            for tag in keywords_with_link}
