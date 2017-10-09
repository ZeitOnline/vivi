from datetime import datetime, timedelta
import mock
import pytz
import transaction
import zeit.content.article.cds
import zeit.content.article.testing


class CDSTest(zeit.content.article.testing.FunctionalTestCase):

    layer = zeit.content.article.testing.CDS_LAYER

    def setUp(self):
        super(CDSTest, self).setUp()
        fs = zeit.content.article.cds.get_cds_filestore('cds-import')

        article_xml = """\
<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
 <head>
   <attribute ns="http://namespaces.zeit.de/CMS/document"
    name="ressort">Wissen</attribute>
 </head>
 <body>
 </body>
</article>
"""

        with fs.create('art1') as f:
            f.write(article_xml)
        fs.move('art1', 'tmp', 'new')

    def test_import_schedules_job_for_deletion(self):
        async = 'zeit.cms.celery.Task._eager_use_session_'
        with mock.patch('zeit.cms.celery.Task.apply_async') as apply_async, \
                mock.patch(async, new=True):
            self.assertEqual(True, zeit.content.article.cds.import_one())

            transaction.commit()

            self.assertIn('eta', apply_async.call_args[1])
            assert apply_async.call_args[1]['eta'] > (
                datetime.now(pytz.UTC) + timedelta(days=2))
