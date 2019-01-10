from zeit.cms.browser.widget import ConvertingRestructuredTextWidget
from zeit.cms.i18n import MessageFactory as _
import json
import zeit.cms.browser.widget
import zeit.cms.interfaces
import zeit.content.article.edit.header
import zeit.content.article.edit.interfaces
import zeit.edit.browser.form
import zeit.edit.browser.landing
import zeit.edit.browser.library
import zeit.edit.browser.view
import zope.cachedescriptors.property
import zope.component
import zope.security


class Empty(object):

    def render(self):
        return u''


class AutoSaveText(zeit.edit.browser.view.Action):

    undo_description = _('auto-save body text')

    text = zeit.edit.browser.view.Form('text')
    paragraphs = zeit.edit.browser.view.Form('paragraphs')

    def update(self):
        __traceback_info__ = (self.paragraphs, self.text)
        if self.paragraphs:
            original_keys = self.context.keys()
            insert_at = original_keys.index(self.paragraphs[0])
        else:
            insert_at = None
        for key in self.paragraphs:
            del self.context[key]
        order = list(self.context.keys())
        self.data['new_ids'] = []
        for new in self.text:
            factory = new['factory']
            text = new['text']
            if not text.strip():
                continue
            factory = zope.component.queryAdapter(
                self.context, zeit.edit.interfaces.IElementFactory,
                name=factory)
            if factory is None:
                factory = zope.component.getAdapter(
                    self.context, zeit.edit.interfaces.IElementFactory,
                    name='p')
            p = factory()
            self.data['new_ids'].append(p.__name__)
            p.text = text
            if insert_at is not None:
                order.insert(insert_at, p.__name__)
                # Next insert is after the paragraph we just inserted.
                insert_at += 1
        if insert_at is not None:
            self.context.updateOrder(order)


class SaveText(AutoSaveText):

    undo_description = _('edit body text')


class Paragraph(object):

    @property
    def cms_module(self):
        if self.request.interaction.checkPermission(
                'zeit.EditContent', self.context):
            return "zeit.content.article.Editable"

    @property
    def text(self):
        return '<%s>%s</%s>' % (
            self.context.type,
            self.context.text,
            self.context.type)


class Intertitle(Paragraph):

    @property
    def text(self):
        return '<h3>%s</h3>' % (self.context.text,)


class LandingZoneBase(zeit.edit.browser.landing.LandingZone):

    uniqueId = zeit.edit.browser.view.Form('uniqueId')

    def create_block(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId, None)
        if content is None:
            raise ValueError(
                _('The object "${name}" does not exist.', mapping=dict(
                    name=self.uniqueId)))
        position = self.get_position_from_order(self.container.keys())
        self.block = zope.component.queryMultiAdapter(
            (self.container, content, position),
            zeit.edit.interfaces.IElement)
        if self.block is None:
            raise ValueError(
                _('Could not create block for "${name}", because I '
                  "don't know which one.", mapping=dict(
                      name=self.uniqueId)))

    def validate_params(self):
        pass


class BodyLandingZone(LandingZoneBase):
    """Handler to drop objects to the body's landing zone."""

    order = 0


class Body(object):

    @zope.cachedescriptors.property.Lazy
    def writeable(self):
        return zope.security.canAccess(self.context, 'add')

    @zope.cachedescriptors.property.Lazy
    def sortable(self):
        return zope.security.canAccess(self.context, 'updateOrder')

    def values(self):
        return self.context.values()

    @property
    def body_css_class(self):
        css_class = ['editable-area']
        if self.sortable:
            css_class.append('action-block-sorter')
        return ' '.join(css_class)


class EditableHeaderArea(object):

    def show_area(self):
        source = zeit.content.article.source.ARTICLE_TEMPLATE_SOURCE.factory
        if not source.allow_header_module(
                zeit.content.article.interfaces.IArticle(self.context)):
            return False
        return True


class Slice(Body):

    @property
    def values(self):
        return self.context.slice(
            self.request.form['start'], self.request.form['end'])


class BlockLandingZone(LandingZoneBase):
    """Handler to drop objects after other objects."""

    order = 'after-context'


class ReplaceAll(zeit.edit.browser.view.Action):

    find = zeit.edit.browser.view.Form('find')
    replace = zeit.edit.browser.view.Form('replace')

    def update(self):
        count = zeit.content.article.edit.interfaces.IFindReplace(
            self.context).replace_all(self.find, self.replace)
        self.reload()
        self.signal(None, 'after-replace-all', count)


class HeaderAreaFactories(zeit.edit.browser.library.BlockFactories):

    @property
    def library_name(self):
        return zeit.content.article.edit.header.HEADER_NAME

    def get_adapters(self):
        return [{
            'name': name,
            'type': name,
            'title': zeit.content.article.edit.header.MODULES.factory.getTitle(
                self.context, name),
            'library_name': self.library_name,
            'params': {},
        } for name in zeit.content.article.edit.header.MODULES(self.context)]

    def sort_block_types(self, items):
        # Use order defined by the source.
        return items


class EditRawXML(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IRawXML).omit(
            '__name__', '__parent__')
    undo_description = _('edit XML block')

    @property
    def prefix(self):
        return 'rawxml.{0}'.format(self.context.__name__)


class EditRawText(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IRawText).omit(
            '__name__', '__parent__', 'xml')
    undo_description = _('edit raw text block')

    @property
    def prefix(self):
        return 'rawtext.{0}'.format(self.context.__name__)


class EditCitation(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.ICitation).omit(
            '__name__', '__parent__', 'xml')
    undo_description = _('edit citation block')

    @property
    def prefix(self):
        return 'citation.{0}'.format(self.context.__name__)


class EditPuzzleForm(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IPuzzleForm).omit(
            '__name__', '__parent__', 'xml')
    undo_description = _('edit puzzle form block')

    @property
    def prefix(self):
        return 'puzzleform.{0}'.format(self.context.__name__)


class EditLiveblog(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.ILiveblog).omit(
            '__name__', '__parent__', 'xml')
    undo_description = _('edit liveblog block')

    @property
    def prefix(self):
        return 'liveblog.{0}'.format(self.context.__name__)


class EditCardstack(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.ICardstack).omit(
            '__name__', '__parent__', 'xml')
    undo_description = _('edit cardstack block')

    @property
    def prefix(self):
        return 'cardstack.{0}'.format(self.context.__name__)


class EditQuiz(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IQuiz).omit(
            '__name__', '__parent__', 'xml')
    undo_description = _('edit quiz block')

    @property
    def prefix(self):
        return 'quiz.{0}'.format(self.context.__name__)


class EditPodcast(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IPodcast).omit(
            '__name__', '__parent__', 'xml')
    undo_description = _('edit podcast block')

    @property
    def prefix(self):
        return 'podcast.{0}'.format(self.context.__name__)


class EditBox(zeit.edit.browser.form.InlineForm):

    legend = None
    undo_description = _('edit box block')
    _form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IBox,
        zeit.content.image.interfaces.IImages)
    omit_fields = ('__name__', '__parent__', 'xml')

    def setUpWidgets(self, *args, **kwargs):
        super(EditBox, self).setUpWidgets(*args, **kwargs)
        self.widgets['subtitle'].vivi_css_class = 'markdown-enabled'

    @property
    def form_fields(self):
        form_fields = self._form_fields.omit(*self.omit_fields)
        form_fields[
            'subtitle'].custom_widget = \
            zeit.cms.browser.widget.MarkdownWidget
        return form_fields


class EditAdplace(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IAdplace).omit(
            '__name__', '__parent__', 'xml')
    undo_description = _('edit adplace block')

    @property
    def prefix(self):
        return 'adplace.{0}'.format(self.context.__name__)


class EditDivision(zeit.edit.browser.form.InlineForm,
                   zeit.cms.browser.form.CharlimitMixin):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IDivision).select('teaser')
    undo_description = _('edit page break')

    @property
    def prefix(self):
        return 'division.{0}'.format(self.context.__name__)

    def setUpWidgets(self, *args, **kw):
        super(EditDivision, self).setUpWidgets(*args, **kw)
        self.set_charlimit('teaser')


class DoubleQuotes(object):

    def __call__(self):
        return json.dumps(
            zeit.content.article.article.DOUBLE_QUOTE_CHARACTERS.pattern)


class EditJobTicker(zeit.edit.browser.form.InlineForm):

    legend = ''
    undo_description = _('edit jobbox ticker')
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IJobTicker).select(
            'feed')

    @property
    def prefix(self):
        return 'jobticker.{0}'.format(self.context.__name__)


class EditMail(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IMail).omit(
            '__name__', '__parent__', 'xml')
    undo_description = _('edit mail block')

    @property
    def prefix(self):
        return 'mail.{0}'.format(self.context.__name__)
