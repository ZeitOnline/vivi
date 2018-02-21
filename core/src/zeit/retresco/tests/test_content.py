from datetime import datetime
from zeit.cms.checkout.helper import checked_out
from zeit.content.article.interfaces import IArticle
import zeit.content.article.article
import zeit.content.author.author
import zeit.content.image.interfaces
import zeit.content.link.interfaces
import zeit.retresco.tag
import zeit.retresco.testing
import zope.schema


class ContentTest(zeit.retresco.testing.FunctionalTestCase):

    def compare(self, interface, original, new, exclude):
        errors = []
        for name in zope.schema.getFieldNames(interface):
            if name in exclude:
                continue
            expected = getattr(original, name)
            try:
                actual = getattr(new, name)
            except Exception, e:
                actual = str(e)
            if expected != actual:
                errors.append('%s: %s != %s' % (name, expected, actual))
        if errors:
            self.fail('\n'.join(errors))

    def test_convert_tms_result_to_cmscontent(self):
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        author = zeit.content.author.author.Author()
        author.firstname = u'William'
        author.lastname = u'Shakespeare'
        self.repository['shake'] = author
        with checked_out(article) as co:
            co.keywords = (zeit.retresco.tag.Tag('Berlin', 'location'),)
            co.authorships = (co.authorships.create(self.repository['shake']),)
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')

        data = zeit.retresco.interfaces.ITMSRepresentation(article)()
        content = zeit.retresco.interfaces.ITMSContent(data)
        self.assertIsInstance(content, zeit.content.article.article.Article)
        self.assertTrue(IArticle.providedBy(content))
        self.compare(
            IArticle, article, content,
            ['xml', 'main_image', 'main_image_variant_name', 'paragraphs'])

    def test_dav_adapter_work_with_ITMSContent(self):
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        zeit.cms.workflow.interfaces.IPublishInfo(article).urgent = True
        zeit.cms.workflow.interfaces.IPublish(article).publish(async=False)
        published = zeit.cms.workflow.interfaces.IPublishInfo(
            article).date_last_published
        self.assertIsInstance(published, datetime)
        data = zeit.retresco.interfaces.ITMSRepresentation(article)()
        content = zeit.retresco.interfaces.ITMSContent(data)

        # Ensure we're not falling back to the original DAV properties.
        del article.__parent__[article.__name__]
        # Usually you wouldn't be able to talk about a deleted object,
        # let alone look at its DAV properties, but the mechanics take this
        # in stride and return "no such property" for any request, which then
        # is translated to the field's default or missing value.
        self.assertEqual(
            None, zeit.cms.workflow.interfaces.IPublishInfo(
                article).date_last_published)

        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        self.assertEqual(published, info.date_last_published)

    def test_IImages_work_with_TMSContent(self):
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        image = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        with checked_out(article) as co:
            zeit.content.image.interfaces.IImages(co).image = image
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')

        data = zeit.retresco.interfaces.ITMSRepresentation(article)()
        content = zeit.retresco.interfaces.ITMSContent(data)
        images = zeit.content.image.interfaces.IImages(content)
        self.assertEqual(image, images.image)
        self.assertEqual(None, images.fill_color)

    def test_quotes_dot_for_elasticsearch_field_names(self):
        data = {
            'doc_type': 'gallery',
            'payload': {'zeit.content.gallery': {'type': 'standalone'}}}
        content = zeit.retresco.interfaces.ITMSContent(data)
        props = zeit.connector.interfaces.IWebDAVProperties(content)
        self.assertEqual('standalone', props[(
            'type', 'http://namespaces.zeit.de/CMS/zeit.content.gallery')])
        self.assertEqual(
            [('type', 'http://namespaces.zeit.de/CMS/zeit.content.gallery')],
            list(props.keys()))

    def test_unknown_type_creates_UnknownResource(self):
        data = {'doc_type': 'nonexistent'}
        content = zeit.retresco.interfaces.ITMSContent(data)
        self.assertTrue(
            zeit.cms.repository.interfaces.IUnknownResource.providedBy(
                content))

    def test_author_finds_its_properties(self):
        author = zeit.content.author.author.Author()
        author.firstname = u'William'
        author.lastname = u'Shakespeare'
        self.repository['shake'] = author
        author = self.repository['shake']
        data = zeit.retresco.interfaces.ITMSRepresentation(author)()
        content = zeit.retresco.interfaces.ITMSContent(data)
        self.assertIsInstance(content, zeit.content.author.author.Author)
        self.compare(
            zeit.content.author.interfaces.IAuthor, author, content, ['xml'])

    def test_link_finds_its_properties(self):
        link = zeit.content.link.link.Link()
        link.url = u'http://example.com/'
        self.repository['link'] = link
        link = self.repository['link']
        data = zeit.retresco.interfaces.ITMSRepresentation(link)()
        content = zeit.retresco.interfaces.ITMSContent(data)
        self.assertIsInstance(content, zeit.content.link.link.Link)
        self.compare(
            zeit.content.link.interfaces.ILink, link, content, ['xml'])
