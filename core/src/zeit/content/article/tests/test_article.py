# coding: utf8
from unittest import mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS
import zeit.cms.content.interfaces
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.cms.section.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zeit.content.image.imagegroup
import zeit.edit.interfaces
import zeit.edit.rule
import zeit.magazin.interfaces
import zope.component
import zope.event
import zope.interface
import zope.lifecycleevent


class WorkflowTest(zeit.content.article.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        self.article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        self.info = zeit.cms.workflow.interfaces.IPublishInfo(self.article)

        sm = zope.component.getSiteManager()
        self.orig_validator = sm.adapters.lookup(
            (zeit.content.article.interfaces.IArticle,),
            zeit.edit.interfaces.IValidator)

        self.validator = mock.Mock()
        zope.component.provideAdapter(
            self.validator,
            adapts=(zeit.content.article.interfaces.IArticle,),
            provides=zeit.edit.interfaces.IValidator)

    def tearDown(self):
        zope.component.getSiteManager().unregisterAdapter(
            required=(zeit.content.article.interfaces.IArticle,),
            provided=zeit.edit.interfaces.IValidator)
        zope.component.provideAdapter(
            self.orig_validator,
            adapts=(zeit.content.article.interfaces.IArticle,),
            provides=zeit.edit.interfaces.IValidator)
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
        self.assertEqual(1, len(article.xml.body.findall('division')))

    def test_article_should_not_mangle_divisions_on_add_to_repository(self):
        article = self.get_article_with_paras()
        self.repository['article'] = article
        self.assertEqual(
            1, len(self.repository['article'].xml.body.findall('division')))

    def test_article_should_not_mangle_divisions_on_checkin(self):
        article = self.get_article_with_paras()
        self.repository['article'] = article
        with checked_out(self.repository['article']):
            pass
        self.assertEqual(
            1, len(self.repository['article'].xml.body.findall('division')))

    def test_article_without_division_should_get_them_on_checkin(self):
        article = self.get_article_with_paras()
        # mangle the xml
        for p in article.xml.body.division.getchildren():
            article.xml.body.append(p)
        article.xml.body.remove(article.xml.body.division)
        self.repository['article'] = article
        with checked_out(self.repository['article']):
            pass
        self.assertEqual(
            2, len(self.repository['article'].xml.body.findall('division')))


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
        image = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        block.references = block.references.create(image)
        self.assertEqual(image, article.main_image.target)

    def test_setting_main_image_is_reflected_inside_body(self):
        article = self.get_article()
        block = self.get_factory(article, 'image')()
        image = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        article.main_image = article.main_image.create(image)
        block = article.body.values()[0]
        self.assertEqual(image, block.references.target)
        self.assertFalse(block.is_empty)

    def test_setting_main_image_works_if_body_does_not_start_with_image(self):
        article = self.get_article()
        image = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
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


class LayoutHeaderByArticleTemplate(
        zeit.content.article.testing.FunctionalTestCase):

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


class DefaultTemplateByContentType(
        zeit.content.article.testing.FunctionalTestCase):

    def test_config_should_define_default_template_for_context(self):
        article = self.get_article()
        source = zeit.content.article.source.ArticleTemplateSource().factory

        has_default = source._provides_default(
            article,
            ['zeit.cms.section.interfaces.IZONContent'])
        self.assertFalse(has_default)

        zope.interface.alsoProvides(article,
                                    zeit.cms.section.interfaces.IZONContent)
        has_default = source._provides_default(
            article,
            ['zeit.cms.section.interfaces.IZONContent'])
        self.assertTrue(has_default)

        article = self.get_article()
        zope.interface.alsoProvides(article,
                                    zeit.magazin.interfaces.IZMOContent)
        has_default = source._provides_default(
            article,
            ['zeit.cms.section.interfaces.IZONContent',
             'zeit.magazin.interfaces.IZMOContent'])
        self.assertTrue(has_default)

    def test_config_should_define_generic_default_for_context(self):
        source = zeit.content.article.source.ArticleTemplateSource().factory
        self.assertEqual(
            ('article', 'inside'),
            source._get_generic_default())

    def test_config_should_provide_defaults(self):
        article = self.get_article()
        source = zeit.content.article.source.ArticleTemplateSource().factory
        zope.interface.alsoProvides(article,
                                    zeit.cms.section.interfaces.IZONContent)
        self.assertEqual(
            ('article', 'default'),
            source.get_default_template(article))

        article = self.get_article()
        source = zeit.content.article.source.ArticleTemplateSource().factory
        zope.interface.alsoProvides(article,
                                    zeit.magazin.interfaces.IZMOContent)
        self.assertEqual(
            ('short', ''),
            source.get_default_template(article))

        article = self.get_article()
        self.assertEqual(
            ('article', 'inside'),
            source.get_default_template(article))

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
        self.assertEqual(
            'original', self.repository['article'].main_image_variant_name)

    def test_checkout_change_variant_name_if_invalid(self):
        article = self.get_article()
        article._create_image_block_in_front()
        article.main_image_variant_name = 'zmo-only'
        self.repository['article'] = article
        with checked_out(self.repository['article']):
            pass
        self.assertEqual(
            'original', self.repository['article'].main_image_variant_name)

    def test_changing_template_should_set_default_header(self):
        article = self.get_article()
        article._create_image_block_in_front()
        article.template = 'column'
        self.repository['article'] = article
        with checked_out(self.repository['article']) as article:
            self.assertEqual(None, article.header_layout)
            article.template = 'article'
            zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
                article, zope.lifecycleevent.Attributes(
                    zeit.content.article.interfaces.IArticle, 'template')))
            self.assertEqual('default', article.header_layout)


def notify_modified(article, field):
    zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
        article, zope.lifecycleevent.Attributes(
            zeit.cms.content.interfaces.ICommonMetadata, field)))


class ArticleXMLReferenceUpdate(
        zeit.content.article.testing.FunctionalTestCase):

    def test_writes_genre_as_attribute(self):
        self.repository['article'] = self.get_article()
        with checked_out(self.repository['article']) as co:
            co.genre = 'nachricht'

        reference = zope.component.queryAdapter(
            self.repository['article'],
            zeit.cms.content.interfaces.IXMLReference, name='related')
        self.assertIn(
            'genre="nachricht"', zeit.cms.testing.xmltotext(reference))


class ArticleElementReferencesTest(
        zeit.content.article.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        self.article = self.get_article()

    def create_empty_portraitbox_reference(self):
        from zeit.content.article.edit.body import EditableBody
        body = EditableBody(self.article, self.article.xml.body)
        portraitbox_reference = body.create_item('portraitbox', 1)
        portraitbox_reference._validate = mock.Mock()
        return portraitbox_reference

    def test_articles_element_references_iterates_over_references(self):
        from zeit.content.portraitbox.portraitbox import Portraitbox
        pbox = Portraitbox()
        self.repository['pbox'] = pbox
        ref = self.create_empty_portraitbox_reference()
        ref.references = pbox
        self.assertEqual([pbox], list(zeit.edit.interfaces.IElementReferences(
            self.article)))

    def test_empty_imagegroup_not_in_element_references(self):
        from zeit.content.article.edit.body import EditableBody
        self.repository['image-group'] = \
            zeit.content.image.imagegroup.ImageGroup()
        body = EditableBody(self.article, self.article.xml.body)
        image_group = body.create_item('image', 3)
        image_group.references = image_group.references.create(
            self.repository['image-group'])
        image_group._validate = mock.Mock()
        self.repository['article_with_empty_ref'] = self.article
        self.assertEqual([], list(zeit.edit.interfaces.IElementReferences(
            self.repository['article_with_empty_ref'])))

    def test_articles_element_references_is_empty_if_no_references_are_set(
            self):
        self.assertEqual([], list(zeit.edit.interfaces.IElementReferences(
            self.article)))

    def test_articles_element_references_is_empty_if_empty_reference_is_set(
            self):
        self.create_empty_portraitbox_reference()
        self.assertEqual([], list(zeit.edit.interfaces.IElementReferences(
            self.article)))
