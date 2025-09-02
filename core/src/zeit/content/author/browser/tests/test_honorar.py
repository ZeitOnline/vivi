# coding: utf-8
from unittest import mock

import pendulum
import transaction
import zope.component

import zeit.content.author.author
import zeit.content.author.browser.honorar as honorar
import zeit.content.author.interfaces
import zeit.content.author.testing
import zeit.find.interfaces
import zeit.retresco.testing


class HonorarLookupTest(zeit.content.author.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.patch = mock.patch('zeit.content.author.author.Author.exists')
        self.author_exists = self.patch.start()
        self.author_exists.return_value = False

    def tearDown(self):
        self.patch.stop()
        super().tearDown()

    def test_add_author_first_searches_honorar_db(self):
        api = zope.component.getUtility(zeit.content.author.interfaces.IHonorar)
        api.search.return_value = [
            {'gcid': '1234', 'vorname': 'Williäm', 'nachname': 'Shakespeare'},
            {'gcid': 2345, 'vorname': 'Random', 'nachname': 'Filler'},
        ]
        b = self.browser
        b.open('http://localhost/++skin++vivi/@@zeit.content.author.lookup')
        b.getControl('Firstname').value = 'föö'
        b.getControl('Lastname').value = 'bar'
        b.getControl('Look up author').click()
        b.getControl(name='selection').displayValue = ['Williäm Shakespeare']
        b.getControl(name='action-import').click()
        self.assertEqual('Williäm', b.getControl('Firstname').value)
        self.assertEqual('Shakespeare', b.getControl('Lastname').value)
        self.assertEqual('1234', b.getControl('Honorar ID').value)

    def test_adding_name_twice_warns_then_creates_different_author(self):
        folder = zeit.cms.content.add.find_or_create_folder(
            'foo', 'bar', 'authors', 'S', 'William_Shakespeare'
        )
        folder['index'] = zeit.content.author.author.Author()
        self.author_exists.return_value = True

        b = self.browser
        b.open('http://localhost/++skin++vivi/@@zeit.content.author.lookup')
        self.assertNotIn('Add duplicate author', b.contents)
        b.getControl('Firstname').value = 'William'
        b.getControl('Lastname').value = 'Shakespeare'
        b.getControl('Look up author').click()
        self.assertEllipsis(
            """\
            ...There were errors...
            ...An author with the given name already exists...
            """,
            b.contents,
        )

        b.getControl('Add duplicate author').selected = True
        b.getControl('Look up author').click()
        self.assertNotIn('There were errors', b.contents)

        # Make sure the new author gets a new __name__ rather than overwriting
        # the existing one.
        b.getControl('VG-Wort ID').value = '9876'
        b.getControl('Redaktionszugehörigkeit').displayValue = ['Print']
        b.getControl(name='form.actions.add').click()

        self.assertEqual(
            'http://localhost/++skin++vivi/repository/foo/bar/authors/S/'
            'William_Shakespeare-2/index/@@view.html',
            b.url,
        )
        self.assertEllipsis(
            """...
            <label for="form.firstname">...
            <div class="widget">William</div>...
            <label for="form.lastname">...
            <div class="widget">Shakespeare</div>...
            <label for="form.vgwort_id">...
            <div class="widget">9876</div>...
            """,
            b.contents,
        )

    def test_pen_name_has_priority(self):
        api = zope.component.getUtility(zeit.content.author.interfaces.IHonorar)
        api.search.return_value = [
            {
                'gcid': '1234',
                'vorname': 'Secret',
                'nachname': 'Identity',
                'kuenstlervorname': 'William',
                'kuenstlernachname': 'Shakespeare',
            },
            {'gcid': '2345', 'vorname': 'Random', 'nachname': 'Filler'},
        ]
        b = self.browser
        b.open('http://localhost/++skin++vivi/@@zeit.content.author.lookup')
        b.getControl('Firstname').value = 'foo'
        b.getControl('Lastname').value = 'bar'
        b.getControl('Look up author').click()
        b.getControl(name='selection').displayValue = ['William Shakespeare']
        b.getControl(name='action-import').click()
        self.assertEqual('William', b.getControl('Firstname').value)
        self.assertEqual('Shakespeare', b.getControl('Lastname').value)
        self.assertEqual('1234', b.getControl('Honorar ID').value)

    def test_checks_for_existing_hdok_id(self):
        exists = zeit.content.author.author.Author()
        exists.hdok_id = 12345
        self.repository['exists'] = exists
        self.repository.connector.search_result = ['http://xml.zeit.de/exists']

        b = self.browser
        b.open('http://localhost/++skin++vivi/@@zeit.content.author.add_contextfree')
        b.getControl('Firstname').value = 'William'
        b.getControl('Lastname').value = 'Shakespeare'
        b.getControl('VG-Wort ID').value = '12345'
        b.getControl('Honorar ID').value = '12345'
        b.getControl('Redaktionszugehörigkeit').displayValue = ['Print']
        b.getControl(name='form.actions.add').click()
        self.assertEllipsis(
            '...Author with honorar ID 12345...redirect_to?unique_id=http://xml.zeit.de/exists...',
            b.contents,
        )


class ReportInvalidGCIDs(zeit.content.author.testing.BrowserTestCase):
    def test_report_for_invalid_gcids_is_csv_download(self):
        b = self.browser
        with mock.patch(
            'zeit.content.author.browser.honorar.HonorarReports.report_invalid_gcid'
        ) as create_content:  # noqa
            create_content.return_value = 'some csv'
            b.open('http://localhost/++skin++vivi/HonorarReports')  # noqa
            self.assertIn(b.headers['content-type'], ('text/csv', 'text/csv;charset=utf-8'))
            now = pendulum.now('UTC').year
            self.assertStartsWith(
                f'attachment; filename="Hdok-geloeschteGCIDs_{now}',
                b.headers['content-disposition'],
            )
            self.assertEllipsis('some csv', b.contents)


class CSVRendering(zeit.content.author.testing.FunctionalTestCase):
    def test_invalid_gcids_api_request_builds_correct_csv_report(self):
        a1 = zeit.content.author.author.Author()
        a1.hdok_id = 123
        self.repository['a1'] = a1
        a2 = zeit.content.author.author.Author()
        a2.hdok_id = 10055333
        self.repository['a2'] = a2
        transaction.commit()

        api = zope.component.getUtility(zeit.content.author.interfaces.IHonorar)
        api.invalid_gcids.return_value = [
            {
                'geloeschtGCID': 123,
                'geloeschtName': 'Doppeltes Lottchen',
                'geloeschtUUID': '2D39CE6F-AD11-4F6B-9471-5A8D3BAFF4D4',
                'konto': 'ext_klippert',
                'refGCID': 321,
                'refName': 'Lottchen',
                'refUUID': '44AA0603-86FA-ED47-8DBE-2589773E130F',
                'ts': '03/03/2023 14:53:22',
            },
            {
                'geloeschtGCID': 789,
                'geloeschtName': 'Zwil Ling',
                'geloeschtUUID': 'A88EC3B5-9E31-1E48-848B-BE5F4EEE1F31',
                'konto': 'ext_klippert',
                'refGCID': 987,
                'refName': 'Zwil Ling',
                'refUUID': '6C3DB770-20DE-BD48-A990-5B0FD1D93F26',
                'ts': '03/03/2023 17:35:56',
            },
            {
                'geloeschtGCID': 456,
                'geloeschtName': 'Dritter Imbunde',
                'geloeschtUUID': 'A88EC3B5-9E31-1E48-848B-BE5F4EEE1F31',
                'konto': 'ext_klippert',
                'refGCID': '',
                'refName': 'Dritter Imbunde',
                'refUUID': '6C3DB770-20DE-BD48-A990-5B0FD1D93F26',
                'ts': '03/03/2023 17:35:56',
            },
        ]

        csv = honorar.HonorarReports.report_invalid_gcid(self)
        expected = (
            'Geloeschte HDok-ID;Vivi-Autorenobjekt zu geloeschter HDok-ID;ggf.'
            ' gueltige HDok-ID;ggf. gueltiges Vivi-Autorenobjekt\n'
            '123;https://www.zeit.de/a1;321;\n'
        )
        self.assertEqual(csv, expected)
