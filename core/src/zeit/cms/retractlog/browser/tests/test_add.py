# -*- coding: utf-8 -*-
from unittest import mock

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.content.add
import zeit.cms.retractlog
import zeit.cms.testing


class TestRetractList(zeit.cms.testing.ZeitCmsBrowserTestCase):
    login_as = 'seo:seopw'

    def test_retractlog_is_accessable_via_repository(self):
        b = self.browser
        b.open('http://localhost:8080/++skin++vivi/repository')
        b.getLink('Retract log').click()
        self.assertTrue(b.url.endswith('/retractlog'))

    def test_retractlog_lists_empty_list(self):
        b = self.browser
        b.open('http://localhost:8080/++skin++vivi/retractlog')
        self.assertTrue('There are no objects in this folder' in b.contents)

    def test_retractlog_lists_job_objects(self):
        # Add one job
        root = self.getRootFolder()
        logfolder = root['retractlog']
        job = zeit.cms.retractlog.retractlog.Job()
        job.title = 'foo'
        logfolder['foo'] = job
        # and test if it is listed in retractlog
        b = self.browser
        b.open('http://localhost:8080/++skin++vivi/retractlog')
        self.assertTrue('foo' in b.contents)
        self.assertFalse('There are no objects in this folder' in b.contents)

    def test_retractlog_job_can_be_added_from_listing_view(self):
        b = self.browser
        b.open('http://localhost:8080/++skin++vivi/retractlog')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Job']
        url = menu.value[0]
        b.open(url)
        self.assertTrue(b.url.endswith('retractlog/@@add.html'))


class TestJobAdd(zeit.cms.testing.ZeitCmsBrowserTestCase):
    login_as = 'seo:seopw'

    def setUp(self):
        super().setUp()
        self.add_content('test', 'foo')

    def add_content(self, foldername, contentname):
        test_folder = zeit.cms.content.add.find_or_create_folder(foldername)
        test_folder[contentname] = ExampleContentType()

    def get_jobs(self):
        root = self.getRootFolder()
        return root['retractlog'].items()

    def add_job(self, url_string):
        b = self.browser
        b.open('http://localhost:8080/++skin++vivi/retractlog/@@add.html')
        textarea = b.getControl('URLs')
        textarea.value = url_string
        b.handleErrors = False
        b.getControl('Add').click()
        return b

    def test_retractlog_job_is_stored(self):
        b = self.add_job('https://www.zeit.de/test/foo')
        jobs = self.get_jobs()
        self.assertFalse('There were errors' in b.contents)
        self.assertEqual(1, len(jobs))
        job = jobs[0][1]
        self.assertEqual(['http://xml.zeit.de/test/foo'], job.urls)

    def test_adding_too_much_urls_shows_error_message(self):
        b = self.add_job('/test/foo\n' * 10)
        self.assertTrue('There were errors' in b.contents)
        self.assertTrue('Value is too long' in b.contents)
        self.assertEqual(0, len(self.get_jobs()))

    def test_adding_invalid_shows_warning_but_creates_job(self):
        self.add_content('other-valid', 'bar')
        b = self.add_job(
            'https://www.zeit.de/test/foo\n'
            + 'https://www.zeit.de/other-valid/bar\n'
            + 'https://www.zeit.de/online/2007/01/Somalia'
        )
        jobs = self.get_jobs()
        job = jobs[0][1]
        self.assertTrue('Job created but invalid urls where found' in b.contents)
        self.assertEqual(
            ['http://xml.zeit.de/test/foo', 'http://xml.zeit.de/other-valid/bar'], job.urls
        )
        self.assertEqual(['http://xml.zeit.de/online/2007/01/Somalia'], job.invalid)

    def test_adding_unkown_urls_is_possible_and_detected(self):
        self.add_job('https://www.zeit.de/test/bar\n')
        jobs = self.get_jobs()
        job = jobs[0][1]
        self.assertEqual(['http://xml.zeit.de/test/bar'], job.unknown)

    def test_adding_start_retract_job(self):
        with mock.patch('zeit.cms.retractlog.retractlog.Job.start') as start:
            self.add_job('https://www.zeit.de/test/foo\n')
            self.assertTrue(start.called)


class TestJobView(zeit.cms.testing.ZeitCmsBrowserTestCase):
    login_as = 'seo:seopw'

    def setUp(self):
        super().setUp()
        # Add content
        test_folder = zeit.cms.content.add.find_or_create_folder('test')
        test_folder['foo'] = ExampleContentType()
        test_folder['bar'] = ExampleContentType()
        # Create test job
        root = self.getRootFolder()
        logfolder = root['retractlog']
        job = zeit.cms.retractlog.retractlog.Job()
        job.title = 'foo'
        logfolder['foo'] = job
        job.urls = ['http://xml.zeit.de/test/foo', 'http://xml.zeit.de/test/bar']
        job.invalid = ['http://xml.zeit.de/online/2007/01/Somalia']
        job.unknown = ['http://xml.zeit.de/test/baz']

    def open(self):
        b = self.browser
        b.open('http://localhost:8080/++skin++vivi/' 'retractlog/foo/@@index.html')
        return b

    def test_job_view_shows_config(self):
        b = self.open()
        self.assertTrue('/test/foo = 410\n' '/test/bar = 410' in b.contents)

    def test_job_view_shows_unknown(self):
        b = self.open()
        self.assertEllipsis(
            '...<h4>Kein bekannter...<ul>...' '<li>http://xml.zeit.de/test/baz</li>...</ul>...',
            b.contents,
        )

    def test_job_view_shows_urls(self):
        b = self.open()
        self.assertEllipsis(
            '...<h4>Urls...<ul>...'
            '<li>http://xml.zeit.de/test/foo</li>...'
            '<li>http://xml.zeit.de/test/bar</li>...</ul>...',
            b.contents,
        )

    def test_job_view_shows_invalid(self):
        b = self.open()
        self.assertEllipsis(
            '...<h4>Darf nicht...<ul>...'
            '<li>http://xml.zeit.de/online/2007/01/Somalia</li>...</ul>...',
            b.contents,
        )
