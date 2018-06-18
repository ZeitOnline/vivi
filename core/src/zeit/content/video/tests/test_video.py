# -*- coding: utf-8 -*-
import lxml.objectify
import pytest
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.content.video.interfaces
import zeit.content.video.testing
import zeit.content.video.video
import zope.component


class TestVideo(zeit.content.video.testing.TestCase):

    def test_security_should_allow_access_to_id_prefix(self):
        import zeit.cms.testing
        import zope.security.management
        from zope.security.proxy import ProxyFactory
        factory = zeit.content.video.testing.video_factory(self)
        factory.next()
        video = factory.next()  # in repository
        zope.security.management.endInteraction()
        with zeit.cms.testing.interaction('zope.mgr'):
            proxied = ProxyFactory(video)
            self.assertEqual('vid', proxied.id_prefix)

    def test_has_advertisement_defaults_to_true(self):
        # For bw-compat to videos imported before we recognized the field.
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        self.assertEqual(True, video.has_advertisement)


@pytest.mark.parametrize(
    'title,supertitle,result', [
        (u'Äch bön oin Börlünär.', u'Kennedy said:',
         u'kennedy-said-aech-boen-oin-boerluenaer'),
        (None, u'Kennedy said:', u'kennedy-said'),
        (u'Äch bön oin Börlünär.', None, u'aech-boen-oin-boerluenaer')])
def test_seo_slug_returns_url_normalized_version_of_title_and_supertitle(
        title, supertitle, result):
    video = zeit.content.video.video.Video()
    video.title = title
    video.supertitle = supertitle
    assert result == video.seo_slug


class TestReference(zeit.content.video.testing.TestCase):

    def setUp(self):
        super(TestReference, self).setUp()
        self.node = lxml.objectify.XML(
            '<block xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            ' xmlns:py="http://codespeak.net/lxml/objectify/pytype"/>')

    def create_video(self, **kw):
        factory = zeit.content.video.testing.video_factory(self)
        factory.next()
        factory.next()  # video is now in repository['video']
        player = zope.component.getUtility(
            zeit.content.video.interfaces.IPlayer)
        player.get_video.return_value.update(kw)

    def update(self, node):
        updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(
            self.repository['video'])
        updater.update(node)

    def test_still_should_be_contained_in_xml_reference(self):
        self.create_video(video_still='http://stillurl')
        self.update(self.node)
        self.assertEqual(
            'http://stillurl', self.node['video-still'].get('src'))

    def test_thumbnail_should_be_contained_in_xml_reference(self):
        self.create_video(thumbnail='http://thumbnailurl')
        self.update(self.node)
        self.assertEqual(
            'http://thumbnailurl', self.node['thumbnail'].get('src'))

    def test_nodes_should_be_removed_from_reference(self):
        self.create_video(
            video_still='http://stillurl', thumbnail='http://thumbnailurl')
        self.update(self.node)
        self.create_video(video_still=None, thumbnail=None)
        self.update(self.node)
        self.assertRaises(AttributeError, lambda: self.node['video-still'])
        self.assertRaises(AttributeError, lambda: self.node['thumbnail'])


class TestAuthorshipsProperty(zeit.content.video.testing.TestCase):

    def test_authorships_property_converts_IAuthor_to_IReference(
            self):
        from zeit.cms.content.interfaces import IReference
        from zeit.content.author.author import Author
        from zeit.content.video.video import Video
        self.repository['author'] = Author()
        video = Video()
        video.authorships = (self.repository['author'],)
        self.assertEqual(
            [True], [IReference.providedBy(x) for x in video.authorships])
        self.assertEqual(
            [self.repository['author']], [x.target for x in video.authorships])

    def test_authorships_property_passes_IReference_without_conversion(self):
        from zeit.cms.content.interfaces import IReference
        from zeit.content.author.author import Author
        from zeit.content.video.video import Video
        self.repository['author'] = Author()
        video = Video()
        video.authorships = (
            video.authorships.create(self.repository['author']),)
        self.assertEqual(
            [True], [IReference.providedBy(x) for x in video.authorships])
        self.assertEqual(
            [self.repository['author']], [x.target for x in video.authorships])
