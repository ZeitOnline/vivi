import zeit.content.audio.testing


class TestAudioForm(zeit.content.audio.testing.BrowserTestCase):
    def add_audio(self):
        self.browser.open('/repository/online/2007/01')
        menu = self.browser.getControl(name='add_menu')
        menu.displayValue = ['Audio']
        self.browser.open(menu.value[0])
        self.browser.getControl('File name').value = 'test-audio'
        self.browser.getControl('Type').displayValue = 'Podcast'
        self.browser.getControl('Title').value = 'Cats episode'
        self.browser.getControl(label='URL', index=0).value = 'http://example.com/cats.mp3'
        self.browser.getControl(label='URL', index=1).value = 'http://ad-free-example.com/cats.mp3'
        self.browser.getControl('Duration').value = 123
        # Podcast specific fields
        self.browser.getControl('Podcast', index=1).value = ['cat-jokes-pawdcast']
        self.browser.getControl('Episode No').value = '1'
        self.browser.getControl('Episode Summary').value = 'summary'
        self.browser.getControl('Episode Notes').value = 'notes'
        self.browser.getControl('Dashboard Link').value = 'http://simplecast.example.dashboard'
        self.browser.getControl('Add').click()
        assert 'There were errors' not in self.browser.contents

    def test_add_form(self):
        self.add_audio()
        self.browser.getLink('Checkin').click()
        self.assertEllipsis(
            """...
            <label for="form.dashboard_link">...
            <div class="widget"><a href="http://simplecast.example.dashboard" target="http://simplecast.example.dashboard">http://simplecast.example.dashboard</a></div>...
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
            """,
            self.browser.contents,
        )
