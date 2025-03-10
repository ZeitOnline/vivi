# -*- coding: utf-8 -*-
import pytest

import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.content.video.interfaces
import zeit.content.video.testing
import zeit.content.video.video


class TestVideo(zeit.content.video.testing.TestCase):
    def test_has_advertisement_defaults_to_true(self):
        # For bw-compat to videos imported before we recognized the field.
        factory = zeit.content.video.testing.video_factory(self)
        video = next(factory)
        self.assertEqual(True, video.has_advertisement)


@pytest.mark.parametrize(
    'title,supertitle,result',
    [
        ('Äch bön oin Börlünär.', 'Kennedy said:', 'kennedy-said-aech-boen-oin-boerluenaer'),
        (None, 'Kennedy said:', 'kennedy-said'),
        ('Äch bön oin Börlünär.', None, 'aech-boen-oin-boerluenaer'),
    ],
)
def test_seo_slug_returns_url_normalized_version_of_title_and_supertitle(title, supertitle, result):
    video = zeit.content.video.video.Video()
    video.title = title
    video.supertitle = supertitle
    assert result == video.seo_slug


class TestAuthorshipsProperty(zeit.content.video.testing.TestCase):
    def test_authorships_property_converts_IAuthor_to_IReference(self):
        from zeit.cms.content.interfaces import IReference
        from zeit.content.author.author import Author
        from zeit.content.video.video import Video

        self.repository['author'] = Author()
        video = Video()
        video.authorships = (self.repository['author'],)
        self.assertEqual([True], [IReference.providedBy(x) for x in video.authorships])
        self.assertEqual([self.repository['author']], [x.target for x in video.authorships])

    def test_authorships_property_passes_IReference_without_conversion(self):
        from zeit.cms.content.interfaces import IReference
        from zeit.content.author.author import Author
        from zeit.content.video.video import Video

        self.repository['author'] = Author()
        video = Video()
        video.authorships = (video.authorships.create(self.repository['author']),)
        self.assertEqual([True], [IReference.providedBy(x) for x in video.authorships])
        self.assertEqual([self.repository['author']], [x.target for x in video.authorships])
