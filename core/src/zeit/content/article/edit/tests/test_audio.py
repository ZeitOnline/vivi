# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt


import zeit.content.article.testing


class AudioTest(zeit.content.article.testing.FunctionalTestCase):

    def get_audio(self):
        from zeit.content.article.edit.audio import Audio
        import lxml.objectify
        audio = Audio(None, lxml.objectify.E.audio())
        return audio

    def test_audio_id_should_be_set_to_attribute(self):
        audio = self.get_audio()
        audio.audio_id = u'myaudioid'
        self.assertEqual(u'myaudioid', audio.xml.get('audioID'))

    def test_expires_should_be_set_in_xml(self):
        import datetime
        import pytz
        audio = self.get_audio()
        audio.expires = datetime.datetime(2010, 1, 1, tzinfo=pytz.UTC)
        self.assertEqual(u'2010-01-01T00:00:00+00:00',
                         audio.xml.get('expires'))


class TestFactory(zeit.content.article.testing.FunctionalTestCase):

    def test_factory_should_create_audio_node(self):
        import zeit.content.article.article
        import zeit.content.article.edit.interfaces
        import zeit.edit.interfaces
        import zope.component
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, 'audio')
        self.assertEqual('Audio', factory.title)
        div = factory()
        self.assertTrue(
            zeit.content.article.edit.interfaces.IAudio.providedBy(div))
        self.assertEqual('audio', div.xml.tag)
