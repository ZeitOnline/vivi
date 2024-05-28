from unittest import mock

import transaction

from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.newsimport import cli
import zeit.newsimport.testing


def unwrap():
    """set up the importer without `gocept.runner.appmain`"""

    def appmain(**kw):
        def appmain_call(worker):
            def run():
                result = worker()
                transaction.commit()
                return result

            return run

        return appmain_call

    return mock.patch('zeit.cms.cli.runner', side_effect=appmain)


class TestAPIConcoleScript(zeit.newsimport.testing.FunctionalAPITestCase):
    def test_process_task_receives_profile(self):
        args = ['--interval', '30', '--profile', 'nextline']
        with mock.patch('zeit.newsimport.news.process_task') as ptm, unwrap():
            cli.import_dpa_news_api(args=args)
            self.assertEqual(ptm.call_args[0][1], 'nextline')


class TestConcoleScript(zeit.newsimport.testing.FunctionalTestCase):
    def test_import_new_article(self):
        args = ['--interval', '60', '--profile', 'weblines']
        with unwrap():
            zeit.newsimport.cli.import_dpa_news_api(args)
            article = ICMSContent(self.layer['dpa_article_id'])
            transaction.commit()
            self.assertTrue(IPublishInfo(article).published)
            self.assertEqual(11, self.layer['dpa_mock'].delete_entry.call_count)
