# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.content.video.testing


class TestPlaylist(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.video.testing.Layer

    def test_playlist_should_be_viewable(self):
        from zeit.content.video.playlist import Playlist
        pls = Playlist()
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['453'] = pls
        self.browser.open('http://localhost/++skin++vivi/repository/453')
        self.assert_ellipsis("""...
<...
   <label for="form.__name__">
           <span>File name</span>
         </label>...
        <div class="widget">453</div>...
                             """)
