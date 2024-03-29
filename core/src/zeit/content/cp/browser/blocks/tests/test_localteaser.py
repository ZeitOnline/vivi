import zeit.content.cp
import zeit.content.cp.centerpage
import zeit.content.cp.testing


class TestLocalTeaser(zeit.content.cp.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.centerpage = zeit.content.cp.centerpage.CenterPage()
        self.centerpage.body['lead'].create_item('local-teaser')
        self.repository['centerpage'] = self.centerpage
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/centerpage/@@checkout')
        b.open('contents')
        self.content_url = b.url

    def test_can_create_module_via_drag_n_drop_from_sidebar(self):
        b = self.browser
        self.assertEqual(1, b.contents.count('type-local-teaser'))
        b.open('body/lead/@@landing-zone-drop-module?block_type=local-teaser')
        b.open(self.content_url)
        self.assertEqual(2, b.contents.count('type-local-teaser'))

    def test_drag_content_to_module_adds_reference(self):
        b = self.browser
        b.xml_strict = True
        ns = 'http://namespaces.gocept.com/zeit-cms'
        drop = b.cssselect('.type-local-teaser div[cms|drop-url]', namespaces={'cms': ns})[0].get(
            '{%s}drop-url' % ns
        )
        b.open('%s?uniqueId=http://xml.zeit.de/testcontent' % drop)
        b.open(self.content_url)
        self.assertEllipsis(
            """...
  <div class="teaser">...
    <div class="supertitle"></div>
    <div class="teaserTitle"></div>
    <div class="teaserText"></div>
    <span class="uniqueId">http://xml.zeit.de/testcontent</span>
  </div>...""",
            b.contents,
        )

    def test_applies_overrides(self):
        self.test_drag_content_to_module_adds_reference()
        b = self.browser
        form = b.cssselect('.type-local-teaser a.common-link')[0].get('href')
        b.open(form)
        b.getControl('Teaser kicker').value = 'mysuper'
        b.getControl('Teaser title').value = 'mytitle'
        b.getControl('Teaser text').value = 'mytext'
        b.getControl('Apply').click()
        b.open(self.content_url)
        self.assertEllipsis(
            """...
  <div class="teaser">...
    <div class="supertitle">mysuper</div>
    <div class="teaserTitle">mytitle</div>
    <div class="teaserText">mytext</div>
    <span class="uniqueId">http://xml.zeit.de/testcontent</span>
  </div>...""",
            b.contents,
        )
