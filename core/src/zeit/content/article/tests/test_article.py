# coding: utf8
from unittest import mock

import zope.component
import zope.event
import zope.interface
import zope.lifecycleevent

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.workflow.interfaces import (
    CAN_PUBLISH_ERROR,
    CAN_PUBLISH_SUCCESS,
    IPublish,
    IPublishInfo,
)
from zeit.content.article.article import updateTextLengthOnChange
from zeit.content.audio.testing import AudioBuilder
import zeit.cms.config
import zeit.cms.content.interfaces
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.cms.section.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zeit.content.audio.interfaces
import zeit.content.image.imagegroup
import zeit.edit.interfaces
import zeit.edit.rule
import zeit.magazin.interfaces


class WorkflowTest(zeit.content.article.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        self.info = zeit.cms.workflow.interfaces.IPublishInfo(self.article)

        sm = zope.component.getSiteManager()
        self.orig_validator = sm.adapters.lookup(
            (zeit.content.article.interfaces.IArticle,), zeit.edit.interfaces.IValidator
        )

        self.validator = mock.Mock()
        zope.component.provideAdapter(
            self.validator,
            adapts=(zeit.content.article.interfaces.IArticle,),
            provides=zeit.edit.interfaces.IValidator,
        )

    def tearDown(self):
        zope.component.getSiteManager().unregisterAdapter(
            required=(zeit.content.article.interfaces.IArticle,),
            provided=zeit.edit.interfaces.IValidator,
        )
        zope.component.provideAdapter(
            self.orig_validator,
            adapts=(zeit.content.article.interfaces.IArticle,),
            provides=zeit.edit.interfaces.IValidator,
        )
        super().tearDown()

    def test_not_urgent_cannot_publish(self):
        self.assertFalse(self.info.urgent)
        self.assertEqual(CAN_PUBLISH_ERROR, self.info.can_publish())
        self.assertFalse(self.validator.called)

    def test_validation_passes_can_publish(self):
        self.info.urgent = True
        self.validator().status = None
        self.assertEqual(CAN_PUBLISH_SUCCESS, self.info.can_publish())
        self.validator.assert_called_with(self.article)

    def test_validation_fails_cannot_publish(self):
        self.info.urgent = True
        self.validator().status = zeit.edit.rule.ERROR
        self.validator().messages = []
        self.assertEqual(CAN_PUBLISH_ERROR, self.info.can_publish())
        self.validator.assert_called_with(self.article)


class DivisionTest(zeit.content.article.testing.FunctionalTestCase):
    # See bug #9495

    def get_article_with_paras(self):
        article = self.get_article()
        factory = self.get_factory(article, 'p')
        for _ in range(10):
            factory()
        return article

    def test_article_should_not_mangle_divisions_on_create(self):
        article = self.get_article_with_paras()
        self.assertEqual(1, len(article.xml.findall('body/division')))

    def test_article_should_not_mangle_divisions_on_add_to_repository(self):
        article = self.get_article_with_paras()
        self.repository['article'] = article
        self.assertEqual(1, len(self.repository['article'].xml.findall('body/division')))

    def test_article_should_not_mangle_divisions_on_checkin(self):
        article = self.get_article_with_paras()
        self.repository['article'] = article
        with checked_out(self.repository['article']):
            pass
        self.assertEqual(1, len(self.repository['article'].xml.findall('body/division')))

    def test_article_without_division_should_get_them_on_checkin(self):
        article = self.get_article_with_paras()
        body = article.xml.find('body')
        # mangle the xml
        for p in article.xml.find('body/division').getchildren():
            body.append(p)
        body.remove(body.find('division'))
        self.repository['article'] = article
        with checked_out(self.repository['article']):
            pass
        self.assertEqual(2, len(self.repository['article'].xml.findall('body/division')))


class MainImageTest(zeit.content.article.testing.FunctionalTestCase):
    def test_main_image_is_none_if_first_body_is_empty(self):
        article = self.get_article()
        self.assertEqual(None, article.main_image)

    def test_main_image_is_none_if_first_block_is_not_an_image(self):
        article = self.get_article()
        self.get_factory(article, 'p')()
        self.assertEqual(None, article.main_image)

    def test_main_image_is_none_if_first_block_is_an_empty_image(self):
        article = self.get_article()
        self.get_factory(article, 'image')()
        self.assertEqual(None, article.main_image)

    def test_main_image_is_returned_if_first_block_contains_one(self):
        article = self.get_article()
        block = self.get_factory(article, 'image')()
        image = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        block.references = block.references.create(image)
        self.assertEqual(image, article.main_image.target)

    def test_setting_main_image_is_reflected_inside_body(self):
        article = self.get_article()
        block = self.get_factory(article, 'image')()
        image = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        article.main_image = article.main_image.create(image)
        block = article.body.values()[0]
        self.assertEqual(image, block.references.target)
        self.assertFalse(block.is_empty)

    def test_setting_main_image_works_if_body_does_not_start_with_image(self):
        article = self.get_article()
        image = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        article.main_image = article.main_image.create(image)
        block = article.body.values()[0]
        self.assertEqual(image, block.references.target)


class NormalizeQuotes(zeit.content.article.testing.FunctionalTestCase):
    def test_normalize_body_to_inch(self):
        article = self.get_article()
        p = self.get_factory(article, 'p')()
        p.text = '“up” and „down‟ and »around«'
        self.repository['article'] = article
        with checked_out(self.repository['article']) as co:
            block = co.body.values()[0]
            self.assertEqual('"up" and "down" and "around"', block.text)

    def test_normalize_teaser_to_inch(self):
        article = self.get_article()
        article.teaserTitle = '“up” and „down‟ and »around«'
        self.repository['article'] = article
        with checked_out(self.repository['article']) as co:
            self.assertEqual('"up" and "down" and "around"', co.teaserTitle)

    def test_normalize_body(self):
        FEATURE_TOGGLES.set('normalize_quotes')
        article = self.get_article()
        p = self.get_factory(article, 'p')()
        p.text = '“up” and „down‟ and »around«'
        self.repository['article'] = article
        with checked_out(self.repository['article']) as co:
            block = co.body.values()[0]
            self.assertEqual('»up« and »down« and »around«', block.text)

    def test_normalize_teaser(self):
        FEATURE_TOGGLES.set('normalize_quotes')
        article = self.get_article()
        article.teaserTitle = '“up” and „down‟ and »around«'
        self.repository['article'] = article
        with checked_out(self.repository['article']) as co:
            self.assertEqual('»up« and »down« and »around«', co.teaserTitle)


class LayoutHeaderByArticleTemplate(zeit.content.article.testing.FunctionalTestCase):
    def test_header_layout_should_determine_header_module_visibility(self):
        article = self.get_article()
        article.template = 'column'
        article.header_layout = 'default'
        source = zeit.content.article.source.ArticleTemplateSource().factory
        self.assertTrue(source.allow_header_module(article))

    def test_header_layout_should_allow_for_backgroundcolor(self):
        article = self.get_article()
        source = zeit.content.article.source.ArticleHeaderColorSource().factory
        assert source.child_tag == 'color'
        assert '#cccccf' in source.getValues(article)


class DefaultTemplateByContentType(zeit.content.article.testing.FunctionalTestCase):
    def test_config_should_define_default_template_for_context(self):
        article = self.get_article()
        source = zeit.content.article.source.ArticleTemplateSource().factory

        has_default = source._provides_default(article, ['zeit.cms.section.interfaces.IZONContent'])
        self.assertFalse(has_default)

        zope.interface.alsoProvides(article, zeit.cms.section.interfaces.IZONContent)
        has_default = source._provides_default(article, ['zeit.cms.section.interfaces.IZONContent'])
        self.assertTrue(has_default)

        article = self.get_article()
        zope.interface.alsoProvides(article, zeit.magazin.interfaces.IZMOContent)
        has_default = source._provides_default(
            article,
            ['zeit.cms.section.interfaces.IZONContent', 'zeit.magazin.interfaces.IZMOContent'],
        )
        self.assertTrue(has_default)

    def test_config_should_define_generic_default_for_context(self):
        source = zeit.content.article.source.ArticleTemplateSource().factory
        self.assertEqual(('article', 'inside'), source._get_generic_default())

    def test_config_should_provide_defaults(self):
        article = self.get_article()
        source = zeit.content.article.source.ArticleTemplateSource().factory
        zope.interface.alsoProvides(article, zeit.cms.section.interfaces.IZONContent)
        self.assertEqual(('article', 'default'), source.get_default_template(article))

        article = self.get_article()
        source = zeit.content.article.source.ArticleTemplateSource().factory
        zope.interface.alsoProvides(article, zeit.magazin.interfaces.IZMOContent)
        self.assertEqual(('short', ''), source.get_default_template(article))

        article = self.get_article()
        self.assertEqual(('article', 'inside'), source.get_default_template(article))

    def test_article_should_have_default_template_on_checkout(self):
        article = self.get_article()
        self.repository['article'] = article
        with checked_out(self.repository['article']):
            pass
        self.assertEqual('article', self.repository['article'].template)
        self.assertEqual('default', self.repository['article'].header_layout)

    def test_checkout_should_not_change_template_if_already_set(self):
        article = self.get_article()
        article.template = 'column'
        article.header_layout = 'heiter'
        self.repository['article'] = article
        with checked_out(self.repository['article']):
            pass
        self.assertEqual('column', self.repository['article'].template)
        self.assertEqual('heiter', self.repository['article'].header_layout)

    def test_checkout_should_assign_default_if_current_value_invalid(self):
        article = self.get_article()
        article.template = 'nonexistent'
        self.repository['article'] = article
        with checked_out(self.repository['article']):
            pass
        self.assertEqual('article', self.repository['article'].template)

    def test_article_should_have_default_variant_name_on_checkout(self):
        article = self.get_article()
        article._create_image_block_in_front()
        self.repository['article'] = article
        with checked_out(self.repository['article']):
            pass
        self.assertEqual('original', self.repository['article'].main_image_variant_name)

    def test_checkout_change_variant_name_if_invalid(self):
        article = self.get_article()
        article._create_image_block_in_front()
        article.main_image_variant_name = 'zmo-only'
        self.repository['article'] = article
        with checked_out(self.repository['article']):
            pass
        self.assertEqual('original', self.repository['article'].main_image_variant_name)

    def test_changing_template_should_set_default_header(self):
        article = self.get_article()
        article._create_image_block_in_front()
        article.template = 'column'
        self.repository['article'] = article
        with checked_out(self.repository['article']) as article:
            self.assertEqual(None, article.header_layout)
            article.template = 'article'
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(
                    article,
                    zope.lifecycleevent.Attributes(
                        zeit.content.article.interfaces.IArticle, 'template'
                    ),
                )
            )
            self.assertEqual('default', article.header_layout)


class ArticleElementReferencesTest(zeit.content.article.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.article = self.get_article()

    def create_empty_portraitbox_reference(self):
        from zeit.content.article.edit.body import EditableBody

        body = EditableBody(self.article, self.article.xml.find('body'))
        portraitbox_reference = body.create_item('portraitbox', 1)
        portraitbox_reference._validate = mock.Mock()
        return portraitbox_reference

    def test_articles_element_references_iterates_over_references(self):
        from zeit.content.portraitbox.portraitbox import Portraitbox

        pbox = Portraitbox()
        self.repository['pbox'] = pbox
        ref = self.create_empty_portraitbox_reference()
        ref.references = pbox
        self.assertEqual([pbox], list(zeit.edit.interfaces.IElementReferences(self.article)))

    def test_empty_imagegroup_not_in_element_references(self):
        from zeit.content.article.edit.body import EditableBody

        self.repository['image-group'] = zeit.content.image.imagegroup.ImageGroup()
        body = EditableBody(self.article, self.article.xml.find('body'))
        image_group = body.create_item('image', 3)
        image_group.references = image_group.references.create(self.repository['image-group'])
        image_group._validate = mock.Mock()
        self.repository['article_with_empty_ref'] = self.article
        self.assertEqual(
            [],
            list(
                zeit.edit.interfaces.IElementReferences(self.repository['article_with_empty_ref'])
            ),
        )

    def test_articles_element_references_is_empty_if_no_references_are_set(self):
        self.assertEqual([], list(zeit.edit.interfaces.IElementReferences(self.article)))

    def test_articles_element_references_is_empty_if_empty_reference_is_set(self):
        self.create_empty_portraitbox_reference()
        self.assertEqual([], list(zeit.edit.interfaces.IElementReferences(self.article)))


class ArticleSpeechbertTest(zeit.content.article.testing.FunctionalTestCase):
    def test_checksum_updates_on_publish(self):
        article = self.get_article()
        article.body.create_item('p').text = 'foo'
        article = self.repository['article'] = article
        with checked_out(article) as co:
            IPublishInfo(co).urgent = True
        IPublish(article).publish()

        checksum = zeit.content.article.interfaces.ISpeechbertChecksum(self.repository['article'])
        first = checksum.checksum
        assert len(first) == 32

        article = self.repository['article']
        article.body.create_item('p').text = 'bar'
        article = self.repository['article'] = article
        IPublish(article).publish()

        second = checksum.checksum
        assert len(second) == 32
        assert second != first

    def test_no_body_does_not_break(self):
        article = self.repository['article'] = self.get_article()
        IPublishInfo(self.repository['article']).urgent = True
        IPublish(article).publish()
        checksum = zeit.content.article.interfaces.ISpeechbertChecksum(self.repository['article'])
        assert checksum.checksum == 'd751713988987e9331980363e24189ce'

    def test_no_checksum_for_ignored_genres(self):
        uid = 'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept'
        article = self.repository['article'] = zeit.cms.interfaces.ICMSContent(uid)
        zeit.cms.config.set('zeit.workflow', 'speechbert-ignore-genres', 'rezept-vorstellung')
        IPublish(article).publish()
        checksum = zeit.content.article.interfaces.ISpeechbertChecksum(self.repository['article'])
        assert not checksum.checksum


class AudioArticle(zeit.content.article.testing.FunctionalTestCase):
    def _add_audio_to_article(self):
        self.repository['article'] = self.article
        with checked_out(self.article) as co:
            audios = zeit.content.audio.interfaces.IAudioReferences
            audios(co).items = (self.repository['audio'],)
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(
                    co, zope.lifecycleevent.Attributes(audios, 'items')
                )
            )
        self.article = self.repository['article']

    def setUp(self):
        super().setUp()
        self.article = self.get_article()
        self.article.title = ''
        self.article.body.create_item('image')
        self.audio = AudioBuilder().build(self.repository)
        self.info = zeit.content.audio.interfaces.IPodcastEpisodeInfo(self.audio)

    def test_filter_audios_by_audio_type(self):
        self.repository['article'] = self.article
        tts = AudioBuilder().with_audio_type('tts').build(self.repository, 'tts')
        pc1 = AudioBuilder().with_audio_type('podcast').build(self.repository, 'pc1')
        pc2 = AudioBuilder().with_audio_type('podcast').build(self.repository, 'pc2')
        audios_refs = zeit.content.audio.interfaces.IAudioReferences(self.article)
        audios_refs.add(tts)
        audios_refs.add(pc1)
        audios_refs.add(pc2)
        audios_tts = audios_refs.get_by_type('tts')
        audios_pcs = audios_refs.get_by_type('podcast')
        assert len(audios_tts) == 1
        assert audios_tts[0].uniqueId == 'http://xml.zeit.de/tts'
        assert len(audios_pcs) == 2
        assert audios_pcs[0].uniqueId == 'http://xml.zeit.de/pc1'
        assert audios_pcs[1].uniqueId == 'http://xml.zeit.de/pc2'

    def test_remove_audio_from_article(self):
        self.repository['article'] = self.article
        with checked_out(self.article) as co:
            audios = zeit.content.audio.interfaces.IAudioReferences
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(
                    co, zope.lifecycleevent.Attributes(audios, 'items')
                )
            )
        # without items, no changes
        assert 'podcast' != self.article.header_layout

    def test_podcast_updates_article_information(self):
        self._add_audio_to_article()

        assert 'podcast' == self.article.header_layout
        assert self.audio.title == self.article.title
        assert self.audio.title == self.article.teaserTitle
        assert self.info.summary == self.article.teaserText
        assert self.info.podcast.id == self.article.serie.url
        # NOTE: The notes contain html tags
        assert self.info.notes[3:-4] == self.article.body.values()[1].text

    def test_podcast_will_not_replace_existing_values(self):
        self.article.title = 'Do not replace me'
        self.article.teaserTitle = 'Do not replace me'
        self.article.subtitle = 'Do not replace me'
        self.article.teaserText = 'Do not replace me'
        self.article.body.create_item('p')
        self.article.body.create_item('p').text = 'bar'
        self.article.serie = (
            zeit.cms.content.interfaces.ICommonMetadata['serie'].source(None).find('Autotest')
        )
        self._add_audio_to_article()

        assert 'podcast' == self.article.header_layout
        assert self.audio.title != self.article.title
        assert self.audio.title != self.article.teaserTitle
        assert self.info.summary != self.article.teaserText
        assert self.info.notes != self.article.body.values()[1].text
        assert self.info.podcast.id != self.article.serie.url

    def test_other_than_podcast_type_does_not_edit_content(self):
        AudioBuilder().with_audio_type('premium').build(self.repository)
        self._add_audio_to_article()

        assert 'podcast' == self.article.header_layout
        assert self.audio.title != self.article.title
        assert self.info.summary != self.article.teaserText
        assert len(self.article.body.values()) == 1, (
            'Without audio, body should only contain "main image block"'
        )

    def test_article_body_contains_all_warped_html_formats(self):
        p0 = 'I am a paragraph without the paragraph tags!'
        p1 = 'We can <b>use Markdown</b> and <a href="https://example.com">Links</a>'
        p2 = 'But wait there is more, like <i>lists:</i>'
        ol = '<li>ü</li><li>käse</li><li>a b c</li>'
        h = 'lalala'
        notes = f'{p0}<p>{p1}</p><p>{p2}</p><ul>{ol}</ul><h1>{h}</h1>'
        audio = self.repository['audio']
        with checked_out(audio) as co:
            info = zeit.content.audio.interfaces.IPodcastEpisodeInfo(co)
            info.notes = notes
        self._add_audio_to_article()
        assert self.article.body.values()[1].text == p0
        assert self.article.body.values()[2].text == p1
        assert self.article.body.values()[3].text == p2
        assert self.article.body.values()[4].text == ol
        assert self.article.body.values()[5].text == h


class ArticleProperties(zeit.content.article.testing.FunctionalTestCase):
    def test_article_text_length_is_updated_on_change(self):
        article = self.get_article()
        article.textLength = 0
        updateTextLengthOnChange(article, object())
        assert article.textLength == 37


class ArticleSearchableText(zeit.content.article.testing.FunctionalTestCase):
    def test_article_get_searchable_text(self):
        article = self.get_article()
        article.body.create_item('p').text = '<a href="http://foo">Link</a> und mehr Text</p>'
        article.body.create_item('p').text = ''
        article.body.create_item('p').text = 'Normaler Absatz'
        adapter = zope.index.text.interfaces.ISearchableText(article)
        assert adapter.getSearchableText() == ['Link', 'und mehr Text', 'Normaler Absatz']


class WochenmarktArticles(zeit.content.article.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        FEATURE_TOGGLES.set('wcm_19_store_recipes_in_storage')
        uid = 'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept'
        self.repository['article'] = zeit.cms.interfaces.ICMSContent(uid)

    def test_recipe_properties_are_stored(self):
        with checked_out(self.repository['article']):
            pass
        article = self.repository['article']
        self.assertEqual(2, len(article.recipe_categories))
        self.assertEqual(('Wurst-Hähnchen', 'Tomaten-Grieß'), article.recipe_titles)
        self.assertEqual(
            ['brathaehnchen', 'bratwurst', 'chicken-nuggets', 'gurke', 'tomate'],
            sorted(article.recipe_ingredients),
        )

    def test_recipe_category_is_added_on_checkin(self):
        ingredients = zeit.wochenmarkt.sources.ingredientsSource(None).factory
        with checked_out(self.repository['article']) as co:
            recipelist = co.body.filter_values(zeit.content.modules.interfaces.IRecipeList)
            for recipe in recipelist:
                recipe.ingredients = [
                    i
                    for i in recipe.ingredients
                    if ingredients.find(None, i.id) and ingredients.find(None, i.id).diet == 'vegan'
                ]

        article = self.repository['article']
        self.assertEqual(3, len(article.recipe_categories))
        self.assertEqual('vegane-rezepte', article.recipe_categories[2].id)
        self.assertEqual(('Wurst-Hähnchen', 'Tomaten-Grieß'), article.recipe_titles)
        self.assertEqual(
            ['gurke', 'tomate'],
            sorted(article.recipe_ingredients),
        )

    def test_recipe_category_is_added_on_checkin_with_multiple_diets(self):
        ingredients = zeit.wochenmarkt.sources.ingredientsSource(None).factory
        with checked_out(self.repository['article']) as co:
            recipelist = co.body.filter_values(zeit.content.modules.interfaces.IRecipeList)
            for recipe in recipelist:
                recipe.ingredients = [
                    i
                    for i in recipe.ingredients
                    if ingredients.find(None, i.id)
                    and ingredients.find(None, i.id).diet in ('vegan', 'vegetarian')
                ] + [ingredients.find(None, 'ei')]
        article = self.repository['article']
        self.assertEqual(3, len(article.recipe_categories))
        self.assertEqual('vegetarische-rezepte', article.recipe_categories[2].id)
        self.assertEqual(('Wurst-Hähnchen', 'Tomaten-Grieß'), article.recipe_titles)
        self.assertEqual(
            ['ei', 'gurke', 'tomate'],
            sorted(article.recipe_ingredients),
        )
