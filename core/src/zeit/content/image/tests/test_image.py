import pytest
import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.content.image.testing import create_image_group, create_local_image
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.content.image.image
import zeit.content.image.testing


class TestImageMetadataAcquisition(zeit.content.image.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.group_id = create_image_group().uniqueId
        with zeit.cms.checkout.helper.checked_out(self.group) as co:
            metadata = zeit.content.image.interfaces.IImageMetadata(co)
            metadata.title = 'Title'

    @property
    def group(self):
        return zeit.cms.interfaces.ICMSContent(self.group_id)

    @property
    def img(self):
        return self.group['new-hampshire-450x200.jpg']

    def test_acquired_in_repository(self):
        metadata = zeit.content.image.interfaces.IImageMetadata(self.img)
        self.assertEqual('Title', metadata.title)

    def test_acquired_in_workingcopy(self):
        with zeit.cms.checkout.helper.checked_out(self.img) as co:
            metadata = zeit.content.image.interfaces.IImageMetadata(co)
            self.assertEqual('Title', metadata.title)
            metadata.title = 'Image title'
        metadata = zeit.content.image.interfaces.IImageMetadata(self.img)
        self.assertEqual('Image title', metadata.title)

    def test_in_workingcopy_when_removed_in_repository(self):
        co = zeit.cms.checkout.interfaces.ICheckoutManager(self.img).checkout()
        del self.group[self.img.__name__]
        metadata = zeit.content.image.interfaces.IImageMetadata(co)
        self.assertEqual(None, metadata.title)


class TestImageXMLReference(zeit.content.image.testing.FunctionalTestCase):
    def test_master_image_without_filename_extension_sets_mime_as_type(self):
        image = zeit.content.image.image.LocalImage()
        with image.open('w') as out:
            with self.repository['2006']['DSC00109_2.JPG'].open() as fh:
                out.write(fh.read())
        self.repository['example-image'] = image
        ref = zope.component.getAdapter(
            self.repository['example-image'],
            zeit.cms.content.interfaces.IXMLReference,
            name='image',
        )
        self.assertEqual('jpeg', ref.get('type'))


class TestImageMIMEType(zeit.content.image.testing.FunctionalTestCase):
    def test_ignores_stored_dav_mime_type(self):
        self.repository['image'] = create_local_image('opernball.jpg')
        with checked_out(self.repository['image']) as co:
            props = zeit.connector.interfaces.IWebDAVProperties(co)
            props[('getcontenttype', 'DAV:')] = 'image/png'
        self.assertEqual('image/jpeg', self.repository['image'].mimeType)


@pytest.mark.parametrize(
    'data',
    [
        {
            'xapmeta': {
                'xaptk': 'XMP toolkit 2.8.2-33, framework 1.5',
                'RDF': {
                    'Description': [
                        {
                            'about': 'uuid:8aa37c89-253f-11d6-8188-bc0c565c2f2f',
                            'City': 'Mainz',
                            'State': 'Rheinland-Pfalz',
                            'Country': 'Deutschland',
                            'Credit': 'picture alliance/dpa',
                            'Source': 'dpa',
                            'CaptionWriter': 'ade flm',
                            'Category': 'New',
                            'Headline': 'Untersuchungsausschuss zur Flutkatastrophe im Ahrtal',
                        },
                        {
                            'about': 'uuid:8aa37c89-253f-11d6-8188-bc0c565c2f2f',
                            'CreateDate': '2022-07-08T02:00:00+00:00',
                        },
                        {'about': 'uuid:8aa37c89-253f-11d6-8188-bc0c565c2f2f', 'Marked': 'True'},
                        {
                            'about': 'uuid:8aa37c89-253f-11d6-8188-bc0c565c2f2f',
                            'creator': {'Seq': {'li': 'Arne Dedert'}},
                            'subject': {
                                'Bag': {
                                    'li': [
                                        'AKTENTASCHE',
                                        'DEUTSCHLAND',
                                        'ermittlungen',
                                        'Hochwasser',
                                        'Katastrophen',
                                        'Landtag',
                                        'LRS',
                                        'Porträt',
                                        'RHEINLAND-PFALZ',
                                        'RHS',
                                        'Vermischtes',
                                        'Politik',
                                    ]
                                }
                            },
                            'description': {
                                'Alt': {
                                    'li': {
                                        'lang': 'x-default',
                                        'text': 'Jürgen Pföhler (CDU), ehemaliger Landrat des '
                                        + 'Kreises Ahrweiler, nimmt als Zeuge im '
                                        + 'Untersuchungsausschuss des Landtags Rheinland-Pfalz '
                                        + 'zur Flutkatastrophe Platz. Der Untersuchungsausschuss '
                                        + 'befasst sich mit der Frage, ob die extreme Wetterlage '
                                        + 'vorhersehbar war und wieso es zu einer solchen '
                                        + 'Zerstörung mit mindestens 135 Toten und Hunderten '
                                        + 'Verletzten kommen konnte. +++ dpa-Bildfunk +++',
                                    }
                                }
                            },
                            'rights': {
                                'Alt': {'li': {'lang': 'x-default', 'text': 'picture alliance/dpa'}}
                            },
                            'title': {'Alt': {'li': {'lang': 'x-default', 'text': '299825378'}}},
                        },
                        {
                            'CountryCode': 'DEU',
                            'CreatorContactInfo': {'parseType': 'Resource', 'text': '\n'},
                        },
                    ]
                },
            }
        },
        {
            'xmpmeta': {
                'xmptk': 'Adobe XMP Core 9.1-c003 79.9690a87fc, 2025/03/06-20:50:16        ',
                'RDF': {
                    'Description': {
                        'about': '',
                        'Category': 'A',
                        'Source': 'Getty Images North America',
                        'City': 'Washington',
                        'AuthorsPosition': 'Staff',
                        'CopyrightFlag': 'true',
                        'Country': 'United States',
                        'DateCreated': '2025-06-24',
                        'Credit': 'Getty Images',
                        'TransmissionReference': '776342096',
                        'Headline': 'President Trump Departs Washington For NATO Summit',
                        'URL': 'https://www.gettyimages.com',
                        'Instructions': 'Not Released (NR) ',
                        'CaptionWriter': 'CS / CS',
                        'State': 'DC',
                        'LegacyIPTCDigest': '5FF2EE632CC653FAAFBB70836D2C9692',
                        'ColorMode': '3',
                        'ICCProfile': 'sRGB IEC61966-2.1',
                        'Rights': '2025 Getty Images',
                        'format': 'image/jpeg',
                        'CountryCode': 'USA',
                        'Dlref': 'ydE3ZN9fAEsj8ap7LAuqtQ==',
                        'ImageRank': '2',
                        'AssetID': '2221849504',
                        'WebStatement': 'https://www.gettyimages.com/eula?utm_medium=organic&utm_source=google&utm_campaign=iptcurl',
                        'DataMining': 'http://ns.useplus.org/ldf/vocab/DMI-PROHIBITED-EXCEPTSEARCHENGINEINDEXING',
                        'CreatorTool': 'Adobe Photoshop 26.8 (Macintosh)',
                        'ModifyDate': '2025-06-24T17:27:51+02:00',
                        'CreateDate': '2025-06-24T06:38:43',
                        'MetadataDate': '2025-06-24T17:27:51+02:00',
                        'SerialNumber': '146202102329',
                        'LensInfo': '70/1 200/1 0/0 0/0',
                        'Lens': 'RF70-200mm F2.8 L IS USM Z',
                        'LensSerialNumber': '1511000748',
                        'LensModel': 'RF70-200mm F2.8 L IS USM Z',
                        'DocumentID': 'adobe:docid:photoshop:a2890b13-f117-7a40-b379-5ce42007e646',
                        'InstanceID': 'xmp.iid:b6239f1d-8cb0-4ba8-89e0-e343a39b2dcb',
                        'OriginalDocumentID': '82124B4F5AA25E1122E72185F0AFC803',
                        'SupplementalCategories': {'Bag': {'li': ['GOV', 'POL']}},
                        'title': {'Alt': {'li': {'lang': 'x-default', 'text': '2221849504'}}},
                        'creator': {'Seq': {'li': 'Chip Somodevilla'}},
                        'description': {
                            'Alt': {
                                'li': {
                                    'lang': 'x-default',
                                    'text': 'WASHINGTON, DC - JUNE 24: U.S. President Donald '
                                    + 'Trump speaks to reporters before boarding the Marine One '
                                    + 'presidential helicopter and departing the White House on '
                                    + 'June 24, 2025 in Washington, DC. Less than 12 hours after '
                                    + 'announcing a ceasefire between Israel and Iran, Trump is '
                                    + "traveling to the Netherlands to attend the NATO leaders'"
                                    + 'summit.  (Photo by Chip Somodevilla/Getty Images)',
                                }
                            }
                        },
                        'subject': {
                            'Bag': {
                                'li': [
                                    'Donald Trump - US-Präsident',
                                    'Waffenruhe',
                                    'Politik und Regierung',
                                    'Marine One-Hubschrauber',
                                    'Präsident der USA',
                                    'Regierung',
                                    'Fotografie',
                                    'NATO',
                                    'Politik',
                                    'Journalist',
                                    'Weißes Haus',
                                    'Hubschrauber',
                                    'Niederlande',
                                    'Israel',
                                    'Iran',
                                    'Washington DC',
                                    'USA',
                                    'Farbbild',
                                    'Horizontal',
                                ]
                            }
                        },
                        'rights': {
                            'Alt': {'li': {'lang': 'x-default', 'text': '2025 Getty Images'}}
                        },
                        'Licensor': {
                            'Seq': {
                                'li': {
                                    'LicensorURL': 'https://www.gettyimages.com/detail/2221849504?utm_medium=organic&utm_source=google&utm_campaign=iptcurl'
                                }
                            }
                        },
                        'History': {
                            'Seq': {
                                'li': [
                                    {
                                        'action': 'saved',
                                        'instanceID': ''
                                        + 'xmp.iid:7287a4f3-5437-4bc4-a2d1-9538b088b778',
                                        'when': '2025-06-24T13:35:21+02:00',
                                        'softwareAgent': 'Adobe Photoshop 26.5 (Macintosh)',
                                        'changed': '/',
                                    },
                                    {
                                        'action': 'saved',
                                        'instanceID': ''
                                        + 'xmp.iid:b6239f1d-8cb0-4ba8-89e0-e343a39b2dcb',
                                        'when': '2025-06-24T17:27:51+02:00',
                                        'softwareAgent': 'Adobe Photoshop 26.8 (Macintosh)',
                                        'changed': '/',
                                    },
                                ]
                            }
                        },
                        'PersonInImage': {'Bag': {'li': 'Donald Trump'}},
                    }
                },
            }
        },
    ],
)
def test_editimages_extracts_metadata(data):
    result = zeit.content.image.image.extract_metadata_from_xmp(data)
    assert result['copyright']
    assert result['title']
    assert result['caption']
