import importlib.resources

import pendulum
import zope.app.appsetup.product
import zope.event

from zeit.content.article.article import Article
from zeit.content.article.interfaces import IArticle
from zeit.content.image.testing import create_image
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.connector.filesystem
import zeit.content.author.author
import zeit.content.link.testing
import zeit.find.testing
import zeit.wochenmarkt.testing


def create_fixture(repository):
    article = Article()
    zeit.cms.content.field.apply_default_values(article, IArticle)
    article.year = 2025
    article.title = 'Cookie monster'
    article.ressort = 'Politik'
    article.supertitle = 'Blue'
    article.subtitle = 'It ate all the cookies'
    article.teaserTitle = 'Cookie monster detained'
    article.teaserText = 'No cookies left'
    article.teaserSupertitle = 'Sesame Street News'
    article.copyrights = 'ZEIT'
    article.access = 'free'
    article.serie = (
        zeit.cms.content.interfaces.ICommonMetadata['serie'].source(None).find('Autotest')
    )
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(article))
    repository['article'] = article

    author = zeit.content.author.author.Author()
    author.firstname = 'William'
    author.lastname = 'Shakespeare'
    repository['author'] = author

    repository['imagefolder'] = zeit.cms.repository.folder.Folder()
    image = create_image()
    modified = zeit.cms.workflow.interfaces.IModified(image)
    modified.date_created = pendulum.datetime(2025, 11, 27, 10, 21, 8, 0)
    semantic = zeit.cms.content.interfaces.ISemanticChange(image)
    semantic.last_semantic_change = pendulum.datetime(2025, 11, 27, 10, 21, 8, 0)
    repository['imagefolder']['image'] = image


HERE = importlib.resources.files(__package__)
CONFIG_LAYER = zeit.cms.testing.ProductConfigLayer(
    {
        'topic-redirect-prefix': 'http://www.zeit.de',
        'index-principal': 'zope.user',
        'kpi-fields': f'file://{HERE}/tests/kpi.xml',
        'topicpages-source': f'file://{HERE}/tests/topicpages.xml',
        'topicpage-prefix': '/thema',
    },
    bases=(
        zeit.content.link.testing.CONFIG_LAYER,
        zeit.content.volume.testing.CONFIG_LAYER,
        zeit.wochenmarkt.testing.CONFIG_LAYER,
    ),
)


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(CONFIG_LAYER, features=['zeit.connector.sql.zope'])
_zope_layer = zeit.cms.testing.RawZopeLayer(ZCML_LAYER)
ZOPE_LAYER = zeit.cms.testing.SQLIsolationSavepointLayer(_zope_layer, create_fixture)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)

CELERY_LAYER = zeit.cms.testing.CeleryWorkerLayer(
    zeit.cms.testing.SQLIsolationTruncateLayer(_zope_layer, create_fixture)
)
CELERY_LAYER.queues += ('search',)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER

    def setUp(self):
        super().setUp()


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER


class TagTestHelpers:
    """Helper to prefill DAV-Property used for keywords of a content object."""

    def set_tags(self, content, xml):
        """Prefill DAV-Property for keywords of `content` with `xml`.

        It inserts `xml` into a newly created DAV-property in the
        the 'tagging' namespace. `xml` is a string containing XML
        representing `Tag` objects, which requires `type` and `text`::

            <tag type="Person">Karen Duve</tag>
            <tag type="Location">Berlin</tag>

        """

        dav = zeit.connector.interfaces.IWebDAVProperties(content)
        name, ns = dav_key = zeit.retresco.tagger.KEYWORD_PROPERTY
        dav[dav_key] = """<ns:rankedTags xmlns:ns="{ns}">
        <rankedTags>{0}</rankedTags></ns:rankedTags>""".format(xml, ns=ns)


def create_testcontent():
    content = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
    content.uniqueId = 'http://xml.zeit.de/testcontent'
    content.teaserText = 'teaser'
    content.title = 'title'
    zeit.cms.content.interfaces.IUUID(content).id = 'myid'
    return content
