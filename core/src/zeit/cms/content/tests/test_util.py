# coding: utf8
import unittest

YOUTUBE = """\
<iframe width="560" height="315" src="http://www.youtube.com/embed/qnydFmqHuVo"
frameborder="0" allowfullscreen></iframe>
"""

TWITTER = """\
<raw>
<blockquote class="twitter-tweet" lang="de"><p>"I suffer from short-term memory
loss. It runs in my family. At least I think it does.... Where are they...?"
<a href="https://twitter.com/search/%23Dory">#Dory</a> 😂 🐠</p>&mdash;
Emily Faith Pedone (@nothinbutdream)
<a href="https://twitter.com/nothinbutdream/status/319927139904405504">
4. April 2013</a></blockquote>
<script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>
</raw>
"""


class TestObjectifySoup(unittest.TestCase):

    def test_should_parse_youtube_embed_code(self):
        from ..util import objectify_soup_fromstring
        xml = objectify_soup_fromstring(YOUTUBE)
        self.assertEqual('iframe', xml.tag)

    def test_should_parse_tweet(self):
        from ..util import objectify_soup_fromstring
        xml = objectify_soup_fromstring(TWITTER)
        self.assertEqual('raw', xml.tag)
