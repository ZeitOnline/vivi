# -*- coding: utf-8 -*-
from unittest import mock
from zeit.content.image.browser.imagegroup import CopyrightCompanyPurchaseReport # noqa
import datetime
import json
import zeit.cms.content.add
import zeit.cms.content.sources
import zeit.cms.testing
import zope.component
import zope.interface


ES_RESULT = """[
{"doc_type": "image-group",
 "payload": {"document": {"copyrights": "<pickle>
                                           <tuple>
                                             <unicode>Fotograf Eins</unicode>
                                             <unicode>Agentur Eins</unicode>
                                             <none/>
                                             <none/>
                                             <int>0</int>
                                           </tuple>
                                         </pickle>",
                          "date_first_released":
                             "2023-01-11T11:11:11.111111+00:00"},
             "image": {"master_images": "<pickle>
                                           <tuple>
                                             <tuple>
                                             <unicode>desktop</unicode>
                                               <unicode>image-eins.jpg</unicode>
                                             </tuple>
                                             </tuple>
                                           </pickle>",
                                           "single_purchase": "yes"}},
 "url": "/politik/deutschland/2022-09/my-new-bg-1/"},
{"doc_type": "image-group",
 "payload": {"document": {"copyrights": "<pickle>
                                           <tuple>
                                             <unicode>Fotograf Zwei</unicode>
                                             <unicode>Agentur Zwei</unicode>
                                             <none/>
                                             <none/>
                                             <int>0</int>
                                           </tuple>
                                         </pickle>",
                          "date_first_released":
                             "2023-02-22T22:22:22.222222+00:00"},
             "image": {"master_images": "<pickle>
                                           <tuple>
                                             <tuple>
                                             <unicode>desktop</unicode>
                                               <unicode>image-zwei.jpg</unicode>
                                             </tuple>
                                             </tuple>
                                           </pickle>",
                       "single_purchase": "yes"}},
 "url": "/politik/deutschland/2022-09/my-new-bg-2/"}
]
 """


class ESResultToCSV(zeit.retresco.testing.FunctionalTestCase):

    def test_csv_list_is_generated_from_elastic_result(self):
        elastic = mock.Mock()
        zope.component.getGlobalSiteManager().registerUtility(
            elastic, zeit.find.interfaces.ICMSSearch)
        elastic.search.return_value = zeit.cms.interfaces.Result(
            json.loads(ES_RESULT, strict=False))
        csv_list = CopyrightCompanyPurchaseReport.create_imagegroup_list(self)
        expected = [['publish_date', 'image_number',
                     'copyright infos', 'internal link'],
                    ['2023-01-11 11:11:11', 'image-eins.jpg',
                     'Fotograf Eins/Agentur Eins/None/None/0',
                     'https://vivi.zeit.de/repository/politik/deutschland/2022-09/my-new-bg-1/'], # noqa
                    ['2023-02-22 22:22:22', 'image-zwei.jpg',
                     'Fotograf Zwei/Agentur Zwei/None/None/0',
                     'https://vivi.zeit.de/repository/politik/deutschland/2022-09/my-new-bg-2/']] # noqa
        self.assertEqual(csv_list, expected)
        pass


class SinglePurchaseProperty(zeit.content.image.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        self.group = (
            zeit.content.image.testing.create_image_group_with_master_image())

    def test_image_group_has_single_purchase_property(self):
        meta = zeit.content.image.interfaces.IImageMetadata(self.group)
        self.assertTrue(hasattr(meta, 'single_purchase'))


class PurchaseToCSVDocument(zeit.content.image.testing.BrowserTestCase):

    def test_copyright_purchase_view_is_csv_file_download(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        b = self.browser
        with mock.patch('zeit.content.image.browser.imagegroup'
                        '.CopyrightCompanyPurchaseReport.create_csv') as create_content: # noqa
            create_content.return_value = 'some csv'
            b.open('http://localhost/++skin++vivi/CopyrightCompanyPurchaseReport') # noqa
            self.assertIn(b.headers['content-type'],
                          ('text/csv', 'text/csv;charset=utf-8'))
            self.assertEqual('attachment; '
                             f'filename="copyright-payment-report_{now}.csv"',
                             b.headers['content-disposition'])
            self.assertEllipsis("some csv", b.contents)
