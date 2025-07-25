from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.content.image.testing import create_image_group
from zeit.content.volume.volume import Volume
import zeit.cms.content.add
import zeit.cms.testing
import zeit.content.text.python
import zeit.content.volume.testing


class VolumeBrowserTest(zeit.content.volume.testing.BrowserTestCase):
    def open_add_form(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/@@zeit.content.volume.Add')
        b.getControl('Date of digital publication').value = '2017-01-01'

    def test_add_form_prefills_year_and_volume_from_global_settings(self):
        self.open_add_form()
        b = self.browser
        self.assertEqual('2008', b.getControl('Year').value)
        self.assertEqual('26', b.getControl(name='form.volume').value)

    def test_automatically_sets_location_using_year_and_volume(self):
        self.open_add_form()
        b = self.browser
        b.getControl('Year').value = '2010'
        b.getControl(name='form.volume').value = '2'
        b.getControl('Add').click()
        b.getLink('Checkin').click()
        self.assertEqual(
            'http://localhost/++skin++vivi/repository/2010/02/ausgabe/@@view.html', b.url
        )

    def test_displays_dynamic_form_fields_for_imagegroup_references(self):
        self.open_add_form()
        b = self.browser
        b.getControl('Add').click()
        self.assertEllipsis("""...Portrait...Landscape...iPad...""", b.contents)

    def test_saves_imagegroup_reference_via_dynamic_form_field(self):
        self.repository['imagegroup'] = create_image_group()
        self.open_add_form()
        b = self.browser
        b.getControl('Add').click()
        b.getControl('Landscape', index=0).value = 'http://xml.zeit.de/imagegroup'
        b.getControl('Apply').click()
        b.getLink('Checkin').click()
        self.assertEllipsis(
            '...<span class="uniqueId">http://xml.zeit.de/imagegroup</span>...', b.contents
        )

    def test_saves_imagegroup_for_dependent_project_in_xml(self):
        self.repository['imagegroup'] = create_image_group()
        self.open_add_form()
        b = self.browser
        b.getControl('Year').value = '2010'
        b.getControl(name='form.volume').value = '2'
        b.getControl('Add').click()
        b.getControl('Landscape', index=1).value = 'http://xml.zeit.de/imagegroup'
        b.getControl('Apply').click()
        b.getLink('Checkin').click()
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2010/02/ausgabe')
        xml = volume.xml.find('covers/cover')
        self.assertEqual('landscape', xml.get('id'))
        self.assertEqual('ZMLB', xml.get('product_id'))
        self.assertEqual('http://xml.zeit.de/imagegroup', xml.get('href'))

    def test_displays_warning_if_volume_with_same_name_already_exists(self):
        b = self.browser
        self.open_add_form()
        b.getControl('Year').value = '2010'
        b.getControl(name='form.volume').value = '2'
        b.getControl('Add').click()
        self.open_add_form()
        b.getControl('Year').value = '2010'
        b.getControl(name='form.volume').value = '2'
        b.getControl('Add').click()
        self.assertEqual(
            'http://localhost/++skin++vivi/repository/@@zeit.content.volume.Add', b.url
        )
        self.assertIn('volume with the given name already exists', b.contents)

    def test_ICommonMetadata_can_be_adapted_to_added_volume(self):
        b = self.browser
        self.open_add_form()
        b.getControl('Year').value = '2010'
        b.getControl(name='form.volume').value = '2'
        b.getControl('Add').click()
        content = ExampleContentType()
        content.year = 2010
        content.volume = 2
        content.product = zeit.cms.content.sources.Product('ZEI')
        self.repository['testcontent'] = content
        volume = zeit.content.volume.interfaces.IVolume(content)
        self.assertEqual('http://xml.zeit.de/2010/02/ausgabe', volume.uniqueId)

    def test_adds_centerpage_in_addition_to_volume(self):
        template = zeit.content.text.python.PythonScript()
        template.text = """import zeit.content.cp.centerpage
cp = zeit.content.cp.centerpage.CenterPage()
cp.year = context['volume'].year
cp.volume = context['volume'].volume
__return(cp)"""
        self.repository['ausgabe-cp-template'] = template

        self.open_add_form()
        b = self.browser
        b.getControl('Year').value = '2010'
        b.getControl(name='form.volume').value = '2'
        b.getControl('Add').click()
        cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2010/02/index')
        self.assertTrue(zeit.content.cp.interfaces.ICenterPage.providedBy(cp))
        self.assertEqual(2010, cp.year)
        self.assertEqual(2, cp.volume)

    def test_teaser_attributes_are_contained_in_volume(self):
        self.open_add_form()
        b = self.browser
        b.getControl('Year').value = '2010'
        b.getControl(name='form.volume').value = '2'
        b.getControl('Add').click()
        b.getControl(name='form.title').value = 'Obamas Return'
        b.getControl(name='form.teaser').value = 'Obama returns you to tell about his vacation'
        b.getControl(name='form.background_color').value = 'ff0000'
        b.getControl('Apply').click()
        b.getLink('Checkin').click()
        volume = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2010/02/ausgabe')
        assert volume.title == 'Obamas Return'
        assert volume.teaser == 'Obama returns you to tell about his vacation'
        assert volume.background_color == 'ff0000'


class TestVolumeCoverWidget(zeit.content.volume.testing.SeleniumTestCase):
    def setUp(self):
        super().setUp()
        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        volume.product = zeit.cms.content.sources.Product('ZEI')
        zeit.cms.content.add.find_or_create_folder('2015', '01')
        self.repository['2015']['01']['ausgabe'] = volume

    def test_only_one_cover_add_form_is_visible_at_the_time(self):
        s = self.selenium
        self.open('/repository/2015/01/ausgabe/@@checkout')
        s.waitForElementPresent('css=#choose-cover')
        s.assertCssCount('css=.column-right', 3)
        s.assertNotVisible('css=.fieldname-cover_ZMLB_portrait')
        s.assertVisible('css=.fieldname-cover_ZEI_portrait')
        s.select('id=choose-cover', 'label=Zeit Magazin')
        s.assertVisible('css=.fieldname-cover_ZMLB_portrait')
        s.assertNotVisible('css=.fieldname-cover_ZEI_portrait')

    def test_saves_title_for_each_cover(self):
        s = self.selenium
        volume = self.repository['2015']['01']['ausgabe']
        title_overrides = volume.xml.makeelement('title-overrides')
        text_zei = volume.xml.makeelement('title', {'product_id': 'ZEI'})
        text_zei.text = 'Budgies are cool'
        text_zmlb = volume.xml.makeelement('title', {'product_id': 'ZMLB'})
        text_zmlb.text = 'Kingfishers are eating fish'
        title_overrides.append(text_zei)
        title_overrides.append(text_zmlb)
        volume.xml.append(title_overrides)
        self.repository['2015']['01']['ausgabe'] = volume
        self.open('/repository/2015/01/ausgabe/@@checkout')
        s.waitForElementPresent('css=#choose-cover')
        # Set title of Die Zeit
        s.select('id=choose-cover', 'label=Die Zeit')
        s.assertValue('id=form.title_ZEI', 'Budgies are cool')
        # Set title for Zeit Magazin
        s.select('id=choose-cover', 'label=Zeit Magazin')
        s.assertValue('id=form.title_ZMLB', 'Kingfishers are eating fish')
