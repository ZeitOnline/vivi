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
import zope.interface


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
                'force_mobile_image')
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

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(EditCommon, self).__call__()


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
        self.teasers = []
        self.header_image = None
        for i, content in enumerate(self.context):
            try:
                texts = zope.component.getMultiAdapter(
                    (content, self.request),
                    ITeaserRepresentation,
                    name=getattr(self.context.layout, 'id', ''))
            except zope.component.ComponentLookupError:
                texts = zope.component.getMultiAdapter(
                    (content, self.request),
                    ITeaserRepresentation)
            if i == 0:
                self.header_image = self.get_image(content)

            self.teasers.append(dict(
                texts=texts,
                uniqueId=content.uniqueId))

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
        if images.image is None:
            return
        image = images.image
        if zeit.content.image.interfaces.IImageGroup.providedBy(image):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            return '%s%s/@@raw' % (self.url(repository), image.variant_url(
                image_pattern, thumbnail=True))
        else:
            return self.url(image, '@@raw')


class ITeaserRepresentation(zope.interface.Interface):
    """
    Specifies how a Teaser should be represented on a CP.
    Right now a teaser representation looks like:
    [{css_class: 'supertitle', content: str},
    {css_class: 'teaserTitle', content: str},
    {css_class: 'teaserText', content: str}]
    """


@grok.adapter(
    zeit.cms.interfaces.ICMSContent,
    zope.publisher.interfaces.IPublicationRequest)
@grok.implementer(ITeaserRepresentation)
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


@zope.component.adapter(zeit.cms.interfaces.ICMSContent,
                        zope.publisher.interfaces.IPublicationRequest)
@zope.interface.implementer(ITeaserRepresentation)
def quote_teaser_representation(content, request):
    article = zeit.content.article.interfaces.IArticle(content, None)
    citation = article and article.body.find_first(
        zeit.content.article.edit.interfaces.ICitation)
    if not (article and citation):
        return default_teaser_representation(content, request)
    texts = list()
    texts.append(dict(css_class='supertitle', content=_('')))
    texts.append(dict(css_class='teaserTitle', content=_('Zitat:')))
    texts.append(dict(css_class='teaserText', content=_(citation.text)))
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
        self.context.updateOrder(self.keys)
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
