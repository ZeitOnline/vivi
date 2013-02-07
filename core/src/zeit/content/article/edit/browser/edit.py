# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import json
import zeit.cms.interfaces
import zeit.cms.related.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.edit.browser.form
import zeit.edit.browser.landing
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

    def update(self):
        super(SaveText, self).update()
        self.signal(
            None, 'reload',
            'editable-body', self.url(self.context, '@@contents'))


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
        self.block = zope.component.queryMultiAdapter(
            (self.create_in, content),
            zeit.edit.interfaces.IElement)
        if self.block is None:
            raise ValueError(
                _('Could not create block for "${name}", because I '
                  "don't know which one.", mapping=dict(
                   name=self.uniqueId)))


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

    @property
    def body_css_class(self):
        css_class = ['editable-area']
        if self.sortable:
            css_class.append('action-block-sorter')
        return ' '.join(css_class)


class BlockLandingZone(LandingZoneBase):
    """Handler to drop objects after other objects."""

    order = 'after-context'


class EditRawXML(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IRawXML).omit('__name__')
    undo_description = _('edit XML block')

    @property
    def prefix(self):
        return 'rawxml.{0}'.format(self.context.__name__)


class EditAudio(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IAudio).omit('__name__', 'xml')
    undo_description = _('edit audio block')

    @property
    def prefix(self):
        return 'audio.{0}'.format(self.context.__name__)


class EditCitation(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.ICitation).omit('__name__', 'xml')
    undo_description = _('edit citation block')

    @property
    def prefix(self):
        return 'citation.{0}'.format(self.context.__name__)


class EditDivision(zeit.edit.browser.form.InlineForm):

    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IDivision).select(
            'teaser')
    undo_description = _('edit page break')

    @property
    def prefix(self):
        return 'division.{0}'.format(self.context.__name__)


class DoubleQuotes(object):

    def __call__(self):
        return json.dumps(
            zeit.content.article.article.DOUBLE_QUOTE_CHARACTERS.pattern)
