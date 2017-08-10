from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import grokcore.component as grok
import zeit.cms.browser.form
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.article
import zeit.content.article.edit.citation
import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zeit.edit.browser.view
import zope.cachedescriptors.property
import zope.component
import zope.event
import zope.formlib.form
import zope.lifecycleevent


COLUMN_ID = 'column://'


class EditLayout(object):

    interface = zeit.content.cp.interfaces.ITeaserBlock
    layout_prefix = 'teaser'

    @property
    def image_path(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.cp')
        return config['layout-image-path']

    @property
    def layouts(self):
        source = self.interface['layout'].source(self.context)
        terms = zope.component.getMultiAdapter(
            (source, self.request), zope.browser.interfaces.ITerms)

        result = []
        for layout in source:
            css_class = [layout.id]
            if layout == self.context.layout:
                css_class.append('selected')
            result.append(dict(
                css_class=' '.join(css_class),
                title=layout.title,
                token=terms.getTerm(layout).token,
            ))
        return result


# XXX this cobbles together just enough to combine SubPageForm and GroupedForm
class EditCommon(
        zope.formlib.form.SubPageEditForm,
        zeit.cms.browser.form.WidgetCSSMixin,
        gocept.form.grouped.EditForm):

    form_fields = (
        zeit.content.cp.browser.blocks.block.EditCommon.form_fields +
        zope.formlib.form.FormFields(
            zeit.content.cp.interfaces.ITeaserBlock).select(
                'force_mobile_image', 'text_color', 'overlay_level')
    )
    widget_groups = ()
    field_groups = (
        gocept.form.grouped.RemainingFields(_(''), css_class='fullWidth'),
    )

    close = False

    template = zope.browserpage.ViewPageTemplateFile('teaser.edit-common.pt')

    @property
    def form(self):
        return ''  # our template uses the grouped-form macros instead


class Display(zeit.cms.browser.view.Base):

    base_css_classes = ['teaser-contents action-content-droppable']

    @property
    def css_class(self):
        css = self.base_css_classes[:]
        layout = self.context.layout
        if layout is not None:
            css.append(layout.id)
        return ' '.join(css)

    def update(self):
        teasers = []
        self.header_image = None
        for i, content in enumerate(self.context):
            try:
                texts = zope.component.getMultiAdapter(
                    (content, self.request),
                    zeit.content.cp.interfaces.ITeaserRepresentation,
                    name=getattr(self.context.layout, 'id', ''))
            except zope.component.ComponentLookupError:
                texts = zope.component.getMultiAdapter(
                    (content, self.request),
                    zeit.content.cp.interfaces.ITeaserRepresentation)
            if i == 0:
                self.header_image = self.get_image(content)

            teasers.append(dict(
                texts=texts,
                uniqueId=content.uniqueId))

        columns = zeit.content.cp.interfaces.ITeaserBlockColumns(self.context)
        idx = 0
        self.columns = []
        for amount in columns:
            self.columns.append(teasers[idx:idx + amount])
            idx += amount

    def get_image(self, content, image_pattern=None):
        if image_pattern is None:
            layout = self.context.layout
            if isinstance(layout, zeit.content.cp.layout.NoBlockLayout):
                return
            if not layout.image_pattern:
                return
            image_pattern = layout.image_pattern
        images = zeit.content.image.interfaces.IImages(content, None)
        if images is None:
            preview = zope.component.queryMultiAdapter(
                (content, self.request), name='preview')
            if preview:
                return self.url(preview)
            return
        if not images.image:
            return
        image = images.image
        if zeit.content.image.interfaces.IImageGroup.providedBy(image):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            return '%s%s/@@raw' % (self.url(repository), image.variant_url(
                image_pattern, thumbnail=True))
        else:
            return self.url(image, '@@raw')


@grok.adapter(
    zeit.cms.interfaces.ICMSContent,
    zope.publisher.interfaces.IPublicationRequest)
@grok.implementer(zeit.content.cp.interfaces.ITeaserRepresentation)
def default_teaser_representation(content, request):

    def make_text_entry(metadata, css_class, name=None):
        if name is None:
            name = css_class
        return dict(css_class=css_class, content=getattr(metadata, name))

    texts = []
    metadata = zeit.cms.content.interfaces.ICommonMetadata(
        content, None)
    if metadata is not None:
        supertitle_property = (
            'teaserSupertitle' if metadata.teaserSupertitle
            else 'supertitle')
        texts.append(make_text_entry(
            metadata, 'supertitle', supertitle_property))
        for name in ('teaserTitle', 'teaserText'):
            texts.append(make_text_entry(metadata, name))
    else:
        # General-purpose fallback, mostly to support IAuthor teasers.
        list_repr = zope.component.queryMultiAdapter(
            (content, request),
            zeit.cms.browser.interfaces.IListRepresentation)
        if list_repr is not None:
            texts.append(make_text_entry(
                list_repr, 'teaserTitle', 'title'))
    return texts


def quote_teaser_representation(content, request):
    article = zeit.content.article.interfaces.IArticle(content, None)
    citation = zeit.content.article.edit.citation.find_first_citation(article)
    if not (article and citation):
        return default_teaser_representation(content, request)
    texts = list()
    texts.append(dict(css_class='supertitle', content=''))
    texts.append(dict(css_class='teaserTitle', content='Zitat:'))
    texts.append(dict(css_class='teaserText', content=citation.text))
    return texts


class Drop(zeit.edit.browser.view.Action):
    """Drop a content object on a teaserblock."""

    uniqueId = zeit.edit.browser.view.Form('uniqueId')
    index = zeit.edit.browser.view.Form('index', json=True, default=0)

    def update(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        self.context.insert(self.index, content)
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))
        self.reload()


class EditContents(zeit.cms.browser.view.Base):
    """Edit the teaser list."""

    @zope.cachedescriptors.property.Lazy
    def teasers(self):
        teasers = []
        for content in self.context:
            metadata = zeit.cms.content.interfaces.ICommonMetadata(
                content, None)
            url = None
            if metadata is None:
                editable = False
                title = content.uniqueId
            else:
                editable = True
                title = metadata.teaserTitle
                try:
                    url = self.url(content)
                except TypeError:
                    # For example, IXMLTeaser cannot be viewed that way.
                    pass
            teasers.append(dict(
                css_class='edit-bar teaser',
                deletable=True,
                editable=editable,
                teaserTitle=title,
                uniqueId=content.uniqueId,
                url=url,
                viewable=bool(url),
            ))

        columns = zeit.content.cp.interfaces.ITeaserBlockColumns(self.context)
        if len(columns) == 2:
            left = columns[0]
            teasers.insert(left, dict(
                css_class='edit-bar column-separator',
                deletable=False,
                editable=False,
                teaserTitle=_('^ Left | Right v'),
                uniqueId=COLUMN_ID,
                viewable=False,
            ))

        return teasers


class ChangeLayout(zeit.edit.browser.view.Action):
    """Change the layout of a teaserblock."""

    interface = zeit.content.cp.interfaces.ITeaserBlock

    layout_id = zeit.edit.browser.view.Form('id')

    def update(self):
        layout = zope.component.getMultiAdapter(
            (self.interface['layout'].source(self.context), self.request),
            zope.browser.interfaces.ITerms).getValue(self.layout_id)
        self.context.layout = layout
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))
        self.signal('before-reload', 'deleted', self.context.__name__)
        self.reload()
        self.signal('after-reload', 'added', self.context.__name__)


@zope.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@zope.interface.implementer(zeit.cms.browser.interfaces.IEditViewName)
def teaserEditViewName(context):
    return 'edit-teaser.html'


class UpdateOrder(zeit.edit.browser.view.Action):

    keys = zeit.edit.browser.view.Form('keys', json=True)

    def update(self):
        keys = self.keys
        try:
            left = keys.index(COLUMN_ID)
        except ValueError:
            left = None
        else:
            del keys[left]
            cols = zeit.content.cp.interfaces.ITeaserBlockColumns(self.context)
            cols[0] = left
        self.context.updateOrder(keys)
        zope.event.notify(
            zope.lifecycleevent.ObjectModifiedEvent(self.context))


class Delete(zeit.edit.browser.view.Action):
    """Delete item from TeaserBlock."""

    uniqueId = zeit.edit.browser.view.Form('uniqueId')

    def update(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        self.context.remove(content)
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))
        self.reload()


class Countings(object):

    @zope.cachedescriptors.property.Lazy
    def countings(self):
        try:
            item = iter(self.context).next()
        except StopIteration:
            pass
        else:
            return zeit.cms.content.interfaces.IAccessCounter(item, None)

    @property
    def today(self):
        if self.countings is not None:
            return self.countings.hits or 0

    @property
    def lifetime(self):
        if self.countings is not None:
            return self.countings.total_hits or 0

    @property
    def url(self):
        if self.countings is not None:
            try:
                return self.countings.detail_url
            except AttributeError:
                pass
