# -*- coding: utf-8 -*-
from unittest import mock
from zeit.content.image.browser.imagegroup import CopyrightCompanyPurchaseReport # noqa
from zeit.content.image.interfaces import IImageMetadata
from zeit.cms.workflow.interfaces import IPublishInfo
import datetime
import zeit.cms.content.add
import zeit.cms.content.sources
import zeit.cms.testing


class ESResultToCSV(zeit.content.image.testing.FunctionalTestCase):

    def test_csv_list_is_generated_from_result_set(self):
        from zeit.content.image.testing import (
            create_image_group_with_master_image)
        group = create_image_group_with_master_image()
        zeit.cms.workflow.interfaces.IPublish(group).publish()
        with zeit.cms.checkout.helper.checked_out(group) as co:
            IImageMetadata(co).copyright = (
                'Fotograf Eins', 'Agentur Eins', None, None, 0)
        dfr = IPublishInfo(group).date_first_released.to_datetime_string()
        with mock.patch('zeit.content.image.browser.imagegroup.'
                        'CopyrightCompanyPurchaseReport.'
                        'find_imagegroups') as findimgr:
            self.find_imagegroups = findimgr
            findimgr.return_value = [group]
            csv_list = CopyrightCompanyPurchaseReport.create_imagegroup_list(
                self)

            expected = [['publish_date', 'image_number',
                         'copyright infos', 'internal link'],
                        [dfr, 'master-image.jpg',
                         'Fotograf Eins/Agentur Eins/None/None/0',
                         'https://vivi.zeit.de/repository/group/']]
            self.assertEqual(csv_list, expected)


class PurchaseToCSVDocument(zeit.content.image.testing.BrowserTestCase):

    def test_csv_copyright_purchase_view_is_csv_file_download(self):
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

    def test_csv_image_group_form_has_single_purchase_checkbox(self):
        brwsr = self.browser
        brwsr.open('http://localhost/++skin++cms/repository/@@zeit.content.image.imagegroup.Add') # noqa
        self.assertEllipsis(
            '...name="form.single_purchase" type="checkbox"...',
            brwsr.contents)