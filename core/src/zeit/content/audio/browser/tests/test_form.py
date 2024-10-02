import zeit.content.audio.testing
import zeit.content.image.testing


class TestAudioForm(zeit.content.audio.testing.BrowserTestCase):
    def add_podcast_audio(self):
        self.browser.open('/repository/online/2007/01')
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Audio']
        self.browser.open(menu.value[0])
        self.browser.getControl('File name').value = 'test-audio'
        self.browser.getControl('Type').displayValue = 'Podcast'
        self.browser.getControl('Title').value = 'Cats episode'
        self.browser.getControl(label='URL', index=0).value = 'http://example.com/cats.mp3'
        self.browser.getControl('Duration').value = 123
        # Podcast specific fields
        self.browser.getControl(label='URL ad-free').value = 'http://ad-free-example.com/cats.mp3'
        self.browser.getControl('Podcast', index=1).value = ['cat-jokes-pawdcast']
        self.browser.getControl('Episode No').value = '1'
        self.browser.getControl('Episode Summary').value = 'summary'
        self.browser.getControl('Episode Notes').value = 'notes'
        self.browser.getControl('Dashboard Link').value = 'http://simplecast.example.dashboard'
        self.browser.getControl('Add').click()
        assert 'There were errors' not in self.browser.contents

    def test_add_podcast_form(self):
        self.add_podcast_audio()
        self.browser.getLink('Checkin').click()
        self.assertEllipsis(
            """...
            <label for="form.title">...
            <div class="widget">Cats episode</div>...
            <label for="form.duration">...
            <div class="widget">02:03</div>...
            <label for="form.audio_type">...
            <div class="widget">Podcast</div>...
            <label for="form.url">...
            <div class="widget"><a href="http://example.com/cats.mp3">http://example.com/cats.mp3</a></div>...
            <label for="form.url_ad_free">...
            <div class="widget"><a href="http://ad-free-example.com/cats.mp3">http://ad-free-example.com/cats.mp3</a></div>...
            <label for="form.podcast">...
            <div class="widget">Cat Jokes Pawdcast</div>...
            <label for="form.episode_nr">...
            <div class="widget">1</div>...
            <label for="form.summary">...
            <div class="widget">summary</div>...
            <label for="form.notes">...
            <div class="widget">notes</div>...
            <label for="form.dashboard_link">...
            <div class="widget"><a href="http://simplecast.example.dashboard" target="http://simplecast.example.dashboard">http://simplecast.example.dashboard</a></div>...
            """,
            self.browser.contents,
        )

    def test_add_tts_audio(self):
        self.browser.open('/repository/online/2007/01')
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Audio']
        self.browser.open(menu.value[0])
        self.browser.getControl('File name').value = 'test-audio'
        self.browser.getControl('Type').displayValue = 'Text to Speech'
        self.browser.getControl('Title').value = 'Cat article'
        self.browser.getControl(label='Preview URL').value = 'http://example.com/cats.mp3'
        self.browser.getControl('Duration').value = 123
        # TTS specific fields
        self.browser.getControl(label='URL', index=2).value = 'http://preview-example.com/cats.mp3'
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        uuid = zeit.cms.content.interfaces.IUUID(article)
        self.browser.getControl('Article uuid').value = uuid.id
        self.browser.getControl('Checksum').value = '123foo'
        self.browser.getControl('Add').click()
        assert 'There were errors' not in self.browser.contents

    def test_add_custom_audio(self):
        self.browser.open('/repository/online/2007/01')
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Audio']
        self.browser.open(menu.value[0])
        self.browser.getControl('File name').value = 'count-olaf-audio'
        self.browser.getControl('Type').displayValue = 'Custom Audio'
        group = zeit.content.image.testing.create_image_group()
        self.browser.getControl('Image').value = group.uniqueId
        self.browser.getControl('Title').value = 'Count Olaf takes the Baudelaire children'
        self.browser.getControl(
            'Teaser kicker'
        ).value = 'Count Olaf is back to steal the Pugs fortune'
        self.browser.getControl(
            'Teaser text'
        ).value = 'The Baudelaire orphans are in for a surprise'
        self.browser.getControl('Add').click()
        assert 'There were errors' not in self.browser.contents
        self.browser.getLink('Checkin').click()
        self.assertEllipsis(
            """...
            <label for="form.teaserTitle">...
            <div class="widget">Count Olaf takes the Baudelaire children</div>...
            <label for="form.teaserSupertitle">...
            <div class="widget">Count Olaf is back to steal the Pugs fortune</div>...
            <label for="form.teaserText">...
            <div class="widget">The Baudelaire orphans are in for a surprise</div>...
            <label for="form.image">...
            <div class="widget">...
            <span class="uniqueId">http://xml.zeit.de/image-group/</span>...
            """,
            self.browser.contents,
        )
