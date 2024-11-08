import json
import logging

import zope.cachedescriptors.property
import zope.component
import zope.security

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.browser.interfaces import VideoTagesschauNoResultError
from zeit.content.article.edit.videotagesschau import Video
import zeit.cms.browser.manual
import zeit.cms.browser.widget
import zeit.cms.config
import zeit.cms.interfaces
import zeit.content.article.edit.header
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.content.modules.rawtext
import zeit.contentquery.interfaces
import zeit.edit.browser.form
import zeit.edit.browser.landing
import zeit.edit.browser.library
import zeit.edit.browser.view


log = logging.getLogger(__name__)


class Empty:
    def render(self):
        return ''


class AutoSaveText(zeit.edit.browser.view.Action):
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
                self.context, zeit.edit.interfaces.IElementFactory, name=factory
            )
            if factory is None:
                factory = zope.component.getAdapter(
                    self.context, zeit.edit.interfaces.IElementFactory, name='p'
                )
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
    pass


class Paragraph:
    @property
    def cms_module(self):
        if self.request.interaction.checkPermission('zeit.EditContent', self.context):
            return 'zeit.content.article.Editable'
        return None

    @property
    def text(self):
        return '<%s>%s</%s>' % (self.context.type, self.context.text, self.context.type)


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
                _('The object "${name}" does not exist.', mapping={'name': self.uniqueId})
            )
        position = self.get_position_from_order(self.container.keys())
        self.block = zope.component.queryMultiAdapter(
            (self.container, content, position), zeit.edit.interfaces.IElement
        )
        if self.block is None:
            raise ValueError(
                _(
                    'Could not create block for "${name}", because I ' "don't know which one.",
                    mapping={'name': self.uniqueId},
                )
            )

    def validate_params(self):
        pass


class BodyLandingZone(LandingZoneBase):
    """Handler to drop objects to the body's landing zone."""

    order = 0


class Body:
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


class EditableHeaderArea:
    def show_area(self):
        source = zeit.content.article.source.ARTICLE_TEMPLATE_SOURCE.factory
        if not source.allow_header_module(zeit.content.article.interfaces.IArticle(self.context)):
            return False
        return True


class Slice(Body):
    @property
    def values(self):
        return self.context.slice(self.request.form['start'], self.request.form['end'])


class BlockLandingZone(LandingZoneBase):
    """Handler to drop objects after other objects."""

    order = 'after-context'


class ReplaceAll(zeit.edit.browser.view.Action):
    find = zeit.edit.browser.view.Form('find')
    replace = zeit.edit.browser.view.Form('replace')

    def update(self):
        count = zeit.content.article.edit.interfaces.IFindReplace(self.context).replace_all(
            self.find, self.replace
        )
        self.reload()
        self.signal(None, 'after-replace-all', count)


class ModuleFactories(zeit.edit.browser.library.BlockFactories):
    @property
    def library_name(self):
        return zeit.content.article.edit.body.BODY_NAME

    def get_adapters(self):
        return [
            {
                'name': name,
                'type': name,
                'title': zeit.content.article.edit.body.MODULES.factory.getTitle(
                    self.context, name
                ),
                'library_name': self.library_name,
                'params': {},
            }
            for name in zeit.content.article.edit.body.MODULES(self.context)
        ]

    def sort_block_types(self, items):
        # Use order defined by the source.
        return items


class HeaderAreaFactories(zeit.edit.browser.library.BlockFactories):
    @property
    def library_name(self):
        return zeit.content.article.edit.header.HEADER_NAME

    def get_adapters(self):
        return [
            {
                'name': name,
                'type': name,
                'title': zeit.content.article.edit.header.MODULES.factory.getTitle(
                    self.context, name
                ),
                'library_name': self.library_name,
                'params': {},
            }
            for name in zeit.content.article.edit.header.MODULES(self.context)
        ]

    def sort_block_types(self, items):
        # Use order defined by the source.
        return items


class EditRawXML(zeit.edit.browser.form.InlineForm):
    legend = None
    form_fields = zope.formlib.form.FormFields(zeit.content.article.edit.interfaces.IRawXML).omit(
        '__name__', '__parent__'
    )

    @property
    def prefix(self):
        return 'rawxml.{0}'.format(self.context.__name__)


class EditRawText(
    zeit.content.modules.rawtext.EmbedParameterForm, zeit.edit.browser.form.InlineForm
):
    legend = None
    _form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IRawText
    ).select('text_reference')
    _omit_fields = list(zeit.edit.interfaces.IBlock)

    @property
    def prefix(self):
        return 'rawtext.{0}'.format(self.context.__name__)


class EditEmbed(zeit.cms.browser.manual.FormMixin, zeit.edit.browser.form.InlineForm):
    legend = None
    form_fields = zope.formlib.form.FormFields(zeit.content.article.edit.interfaces.IEmbed).omit(
        '__name__', '__parent__', 'xml'
    )

    @property
    def prefix(self):
        return 'embed.{0}'.format(self.context.__name__)


class EditCitation(zeit.edit.browser.form.InlineForm):
    legend = None
    form_fields = zope.formlib.form.FormFields(zeit.content.article.edit.interfaces.ICitation).omit(
        *list(zeit.edit.interfaces.IBlock)
    )

    @property
    def prefix(self):
        return 'citation.{0}'.format(self.context.__name__)


class EditCitationComment(zeit.edit.browser.form.InlineForm):
    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.ICitationComment
    ).omit(*list(zeit.edit.interfaces.IBlock))

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        comments = zeit.cms.config.required('zeit.content.article', 'zeit-comments-api-url')
        self.widgets['url'].extra = f'data-comments-api-url={comments}'

    @property
    def prefix(self):
        return 'citationcomment.{0}'.format(self.context.__name__)


class VideoTagesschau(zeit.edit.browser.form.InlineForm):
    legend = None
    video = zeit.content.article.edit.interfaces.IVideoTagesschau
    form_fields = zope.formlib.form.FormFields(video).select('tagesschauvideo')

    @property
    def prefix(self):
        return 'videotagesschau.{0}'.format(self.context.__name__)

    # Have to copy, since when adding one @action, we lose any inherited ones.
    @zope.formlib.form.action(_('Apply'), failure='success_handler')
    def handle_edit_action(self, action, data):
        return self.success_handler(action, data)

    @zope.formlib.form.action(_('generate-video-recommendation'))
    def handle_update(self, action, data):
        article = zope.security.proxy.getObject(
            zeit.content.article.interfaces.IArticle(self.context)
        )
        try:
            api = zope.component.getUtility(
                zeit.content.article.edit.interfaces.IVideoTagesschauAPI
            )
            recommendations = []
            for recom in api.request_videos(article)['recommendations']:
                recommendations.append(
                    Video(
                        **{
                            'id': recom.get('program_id'),
                            'title': recom.get('main_title'),
                            'date_published': recom.get('published_start_time'),
                            'video_url_hd': recom['video_uris'].get('hd'),
                            # these values are nice to have but processing should
                            # not fail if they do not exist or have `None` values:
                            'type': (recom.get('search_strategy', '<unknown>') or '<unknown>'),
                            'synopsis': recom.get('short_synopsis', '') or '',
                            'video_url_hls_stream': (
                                recom['video_uris'].get('hlsStream', '') or ''
                            ),
                            'video_url_hq': recom['video_uris'].get('hq', '') or '',
                            'video_url_ln': recom['video_uris'].get('ln', '') or '',
                            'thumbnail_url_large': (recom['thumbnail_uris'].get('large', '') or ''),
                            'thumbnail_url_fullhd': (
                                recom['thumbnail_uris'].get('fullhd', '') or ''
                            ),
                            'thumbnail_url_small': (recom['thumbnail_uris'].get('small', '') or ''),
                            'date_available': (recom.get('start_of_availability', '') or ''),
                        }
                    )
                )
            if recommendations == []:
                self.errors = (VideoTagesschauNoResultError('empty'),)
                self.status = _('There were errors')
            self.context.tagesschauvideos = recommendations
        except Exception as exc:
            log.error(f'ARD-API: {exc}', exc_info=True)
            self.errors = (VideoTagesschauNoResultError('technical'),)
            self.status = _('There were errors')


class EditPuzzleForm(zeit.edit.browser.form.InlineForm):
    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IPuzzleForm
    ).omit(*list(zeit.edit.interfaces.IBlock))

    @property
    def prefix(self):
        return 'puzzleform.{0}'.format(self.context.__name__)


class EditLiveblog(zeit.edit.browser.form.InlineForm):
    legend = None
    form_fields = zope.formlib.form.FormFields(zeit.content.article.edit.interfaces.ILiveblog).omit(
        *list(zeit.edit.interfaces.IBlock)
    )

    @property
    def prefix(self):
        return 'liveblog.{0}'.format(self.context.__name__)


class EditTickarooLiveblog(zeit.edit.browser.form.InlineForm):
    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.modules.interfaces.ITickarooLiveblog
    ).omit(*list(zeit.edit.interfaces.IBlock))


class EditCardstack(zeit.edit.browser.form.InlineForm):
    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.ICardstack
    ).omit(*list(zeit.edit.interfaces.IBlock))

    @property
    def prefix(self):
        return 'cardstack.{0}'.format(self.context.__name__)


class EditQuiz(zeit.edit.browser.form.InlineForm):
    legend = None
    form_fields = zope.formlib.form.FormFields(zeit.content.article.edit.interfaces.IQuiz).omit(
        *list(zeit.edit.interfaces.IBlock)
    )

    @property
    def prefix(self):
        return 'quiz.{0}'.format(self.context.__name__)


class EditBox(zeit.edit.browser.form.InlineForm):
    legend = None
    _form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IBox, zeit.content.image.interfaces.IImages
    )
    omit_fields = list(zeit.edit.interfaces.IBlock)

    def setUpWidgets(self, *args, **kwargs):
        super().setUpWidgets(*args, **kwargs)
        self.widgets['subtitle'].vivi_css_class = 'markdown-enabled'

    @property
    def form_fields(self):
        form_fields = self._form_fields.omit(*self.omit_fields)
        form_fields['subtitle'].custom_widget = zeit.cms.browser.widget.MarkdownWidget
        return form_fields


class EditAdplace(zeit.edit.browser.form.InlineForm):
    legend = None
    form_fields = zope.formlib.form.FormFields(zeit.content.article.edit.interfaces.IAdplace).omit(
        *list(zeit.edit.interfaces.IBlock)
    )

    @property
    def prefix(self):
        return 'adplace.{0}'.format(self.context.__name__)


class EditDivision(zeit.edit.browser.form.InlineForm, zeit.cms.browser.form.CharlimitMixin):
    legend = None
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IDivision
    ).select('teaser')

    @property
    def prefix(self):
        return 'division.{0}'.format(self.context.__name__)

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.set_charlimit('teaser')


class DoubleQuotes:
    def __call__(self):
        self.request.response.setHeader('Cache-Control', 'no-cache')
        return json.dumps(
            {
                'chars': zeit.content.article.article.QUOTE_CHARACTERS.pattern,
                'chars_open': (zeit.content.article.article.QUOTE_CHARACTERS_OPEN.pattern),
                'chars_close': (zeit.content.article.article.QUOTE_CHARACTERS_CLOSE.pattern),
                'normalize_quotes': FEATURE_TOGGLES.find('normalize_quotes'),
            }
        )


class EditJobTicker(zeit.edit.browser.form.InlineForm):
    legend = ''
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IJobTicker
    ).select('feed')

    @property
    def prefix(self):
        return 'jobticker.{0}'.format(self.context.__name__)


class EditMail(zeit.edit.browser.form.InlineForm):
    legend = None
    form_fields = zope.formlib.form.FormFields(zeit.content.article.edit.interfaces.IMail).omit(
        *list(zeit.edit.interfaces.IBlock)
    )

    @property
    def prefix(self):
        return 'mail.{0}'.format(self.context.__name__)


class EditTopicbox(zeit.edit.browser.form.InlineForm, zeit.cms.browser.form.CharlimitMixin):
    legend = None

    @property
    def form_fields(self):
        form_fields = (
            zope.formlib.form.Fields(zeit.content.article.edit.interfaces.ITopicbox)
            .select('supertitle', 'title', 'link', 'link_text')
            .omit(*list(zeit.edit.interfaces.IBlock))
        )
        form_fields += zope.formlib.form.Fields(zeit.content.image.interfaces.IImages).omit(
            *list(zeit.edit.interfaces.IBlock)
        )
        form_fields += (
            zope.formlib.form.Fields(zeit.content.article.edit.interfaces.ITopicbox)
            .select(
                'first_reference',
                'second_reference',
                'third_reference',
                'automatic_type',
                'referenced_cp',
                'elasticsearch_raw_query',
                'elasticsearch_raw_order',
                'referenced_topicpage',
                'topicpage_filter',
                'topicpage_order',
                'preconfigured_query',
            )
            .omit(*list(zeit.edit.interfaces.IBlock))
        )

        if not FEATURE_TOGGLES.find('show_automatic_type_in_topicbox'):
            form_fields = form_fields.omit('automatic_type')

        return form_fields

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.set_charlimit('title')
        self.set_charlimit('supertitle')
        self.set_charlimit('link_text')

    @property
    def prefix(self):
        return 'topicbox.{0}'.format(self.context.__name__)


class EditNewsletterSignup(zeit.edit.browser.form.InlineForm):
    legend = ''
    form_fields = zope.formlib.form.FormFields(
        zeit.content.modules.interfaces.INewsletterSignup
    ).omit(*list(zeit.edit.interfaces.IBlock))
    form_fields['prefix_text'].custom_widget = zeit.cms.browser.widget.MarkdownWidget

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.widgets['prefix_text'].height = 50

    @property
    def prefix(self):
        return 'newsletter.{0}'.format(self.context.__name__)


class EditRecipeList(zeit.edit.browser.form.InlineForm):
    legend = ''
    form_fields = zope.formlib.form.FormFields(zeit.content.modules.interfaces.IRecipeList).omit(
        *list(zeit.edit.interfaces.IBlock)
    )

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.widgets['ingredients'].add_type = zeit.content.article.edit.interfaces.IRecipeList
        self.widgets['ingredients'].display_list_below_buttons = True

    @property
    def prefix(self):
        return 'ingredients.{0}'.format(self.context.__name__)


class EditIngredientDice(zeit.edit.browser.form.InlineForm):
    legend = ''
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IIngredientDice
    ).omit(*list(zeit.edit.interfaces.IBlock))

    @property
    def prefix(self):
        return 'ingredientdice.{0}'.format(self.context.__name__)


class EditAnimation(zeit.cms.browser.manual.FormMixin, zeit.edit.browser.form.InlineForm):
    legend = ''
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.edit.interfaces.IAnimation
    ).omit(*list(zeit.edit.interfaces.IBlock))

    @property
    def prefix(self):
        return 'animation.{0}'.format(self.context.__name__)


class EditImageRow(zeit.edit.browser.form.InlineForm):
    legend = ''
    form_fields = zope.formlib.form.FormFields(zeit.content.article.edit.interfaces.IImageRow).omit(
        *list(zeit.edit.interfaces.IBlock)
    )

    @property
    def prefix(self):
        return 'image_row.{0}'.format(self.context.__name__)
