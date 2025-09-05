import pytest
import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.content.image.testing import (
    create_image_group,
    create_image_group_with_master_image,
    create_local_image,
)
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
        create_image_group_with_master_image()
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


class TestImageProperties(zeit.content.image.testing.FunctionalTestCase):
    def test_image_properties_are_set(self):
        FEATURE_TOGGLES.set('column_read_wcm_56')
        FEATURE_TOGGLES.set('column_write_wcm_56')
        image = create_local_image('opernball.jpg')
        image.mimeType = 'image/jpeg'
        image.width = 119
        image.height = 160
        self.repository['image'] = image
        image = self.repository['image']
        self.assertEqual('image/jpeg', image.mimeType)
        self.assertEqual((119, 160), image.getImageSize())
        self.assertEqual(119, image.width)
        self.assertEqual(160, image.height)
        self.assertEqual(119 / 160, image.ratio)


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
                        'WebStatement': 'https://www.gettyimages.com/eula?utm_medium=organic&',
                        'DataMining': 'http://ns.useplus.org/ldf/vocab/DMI-PROHIBITED-EXCEPTSEARCH',
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
                                    'LicensorURL': 'https://www.gettyimages.com/detail/2221849504?u'
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
        {
            'xmpmeta': {
                'xmptk': 'Image::ExifTool 10.96',
                'RDF': {
                    'Description': [
                        {
                            'about': '',
                            'CountryCode': 'USA',
                            'CreatorContactInfo': {
                                'parseType': 'Resource',
                                'CiAdrCity': 'Anytown',
                                'CiAdrCtry': 'USA',
                                'CiAdrExtadr': '123 Main St',
                                'CiAdrPcode': '12345',
                                'CiAdrRegion': 'Florida',
                                'CiEmailWork': 'joe@joephotographer.com',
                                'CiTelWork': '123-456-7890',
                                'CiUrlWork': 'joephotographer.com',
                            },
                            'IntellectualGenre': 'intelectual genre here',
                            'Location': '123 Main Street',
                            'Scene': {'Bag': {'li': 'IPTC scene'}},
                            'SubjectCode': {'Bag': {'li': 'iptc subject code here'}},
                        },
                        {
                            'about': '',
                            'AOCopyrightNotice': '(c) 2017 Carl Seibert. 954-256-5834',
                            'AOCreator': {'Seq': {'li': 'Carl Seibert'}},
                            'AODateCreated': '2017-05-29T17:19:21-0400',
                            'AddlModelInfo': 'model info',
                            'ArtworkOrObject': {
                                'Bag': {
                                    'li': {
                                        'parseType': 'Resource',
                                        'AOCircaDateCreated': 'Default',
                                        'AOContentDescription': {
                                            'Alt': {'li': {'lang': 'x-default', 'text': 'Default'}}
                                        },
                                        'AOContributionDescription': {
                                            'Alt': {'li': {'lang': 'x-default', 'text': 'Default'}}
                                        },
                                        'AOCopyrightNotice': 'Default',
                                        'AOCreator': {'Seq': {'li': 'Default'}},
                                        'AOCreatorId': {'Seq': {'li': 'Default'}},
                                        'AOCurrentCopyrightOwnerId': 'Default',
                                        'AOCurrentCopyrightOwnerName': 'Default',
                                        'AOCurrentLicensorId': 'Default',
                                        'AOCurrentLicensorName': 'Default',
                                        'AODateCreated': 'Default',
                                        'AOPhysicalDescription': {
                                            'Alt': {'li': {'lang': 'x-default', 'text': 'Default'}}
                                        },
                                        'AOSource': 'Default',
                                        'AOSourceInvNo': 'Default',
                                        'AOSourceInvURL': 'Default',
                                        'AOStylePeriod': {'Bag': {'li': 'Default'}},
                                        'AOTitle': {
                                            'Alt': {'li': {'lang': 'x-default', 'text': 'Default'}}
                                        },
                                    }
                                }
                            },
                            'DigitalSourceType': 'http://cv.iptc.org/newscodes/digitalsourcetype/d',
                            'Event': {'Alt': {'li': {'lang': 'x-default', 'text': 'event here'}}},
                            'LocationCreated': {
                                'Bag': {
                                    'li': {
                                        'parseType': 'Resource',
                                        'City': 'sublocation city here',
                                        'CountryCode': 'sub loc country code',
                                        'CountryName': 'sublocation country',
                                        'ProvinceState': 'sublocation state',
                                        'Sublocation': 'sublocation here',
                                        'WorldRegion': 'world region',
                                    }
                                }
                            },
                            'LocationShown': {
                                'Bag': {
                                    'li': {
                                        'parseType': 'Resource',
                                        'City': 'sublocation city here',
                                        'CountryCode': 'sub loc country code',
                                        'CountryName': 'sublocation country',
                                        'ProvinceState': 'sublocation state',
                                        'Sublocation': 'sublocation here',
                                        'WorldRegion': 'world region',
                                    }
                                }
                            },
                            'MaxAvailHeight': '2000',
                            'MaxAvailWidth': '2000',
                            'ModelAge': {'Bag': {'li': 'model ages'}},
                            'OrganisationInImageCode': {'Bag': {'li': 'Featured org code'}},
                            'OrganisationInImageName': {'Bag': {'li': 'Featured org name'}},
                            'PersonInImage': {'Bag': {'li': 'person shown'}},
                            'RegistryId': {
                                'Bag': {
                                    'li': {
                                        'parseType': 'Resource',
                                        'RegItemId': '123445',
                                        'RegOrgId': 'PLUS',
                                    }
                                }
                            },
                        },
                        {'about': '', 'Rating': '0'},
                        {'about': '', 'Lens': 'Samsung Galaxy S7 Rear Camera'},
                        {
                            'about': '',
                            'creator': {'Seq': {'li': 'Carl Seibert (XMP)'}},
                            'date': {'Seq': {'li': '2017-05-29T17:19:21-0400'}},
                            'description': {
                                'Alt': {
                                    'li': {
                                        'lang': 'x-default',
                                        'text': '(This caption in XMP) This is a metadata test',
                                    }
                                }
                            },
                            'format': 'image/jpeg',
                            'rights': {
                                'Alt': {
                                    'li': {
                                        'lang': 'x-default',
                                        'text': '© Copyright 2017 Carl Seibert (XMP)',
                                    }
                                }
                            },
                            'subject': {
                                'Bag': {
                                    'li': [
                                        'keywords go here',
                                        'keywords* test image metadata',
                                        'Users',
                                        'carl',
                                        'Documents',
                                        'Websites',
                                        'aa',
                                        'carlsite',
                                        'content',
                                        'blog',
                                        'sample',
                                        'templates',
                                        'metadata',
                                        'all',
                                        'fields',
                                        'w',
                                        'ps',
                                        'hist.jpg',
                                    ]
                                }
                            },
                            'title': {
                                'Alt': {'li': {'lang': 'x-default', 'text': 'object name here'}}
                            },
                        },
                        {
                            'about': '',
                            'GPSAltitude': '0/10',
                            'GPSAltitudeRef': '0',
                            'GPSLatitude': '26,34.951N',
                            'GPSLongitude': '80,12.014W',
                        },
                        {
                            'about': '',
                            'ColorClass': '0',
                            'EditStatus': 'edit status',
                            'PMVersion': 'PM5',
                            'Prefs': '0:0:0:-00001',
                            'Tagged': 'False',
                        },
                        {
                            'about': '',
                            'AuthorsPosition': 'stf',
                            'CaptionWriter': 'jp',
                            'Category': 'Category',
                            'City': 'Anytown',
                            'Country': 'United States',
                            'Credit': 'credit here',
                            'DateCreated': '2017-05-29T17:19:21-04:00',
                            'Headline': 'This is the headline field',
                            'Source': 'source here',
                            'State': 'Florida',
                            'SupplementalCategories': {
                                'Bag': {'li': ['suppcat 1', 'suppcat 2', 'suppcat 3']}
                            },
                            'TransmissionReference': 'trans ref here',
                            'Urgency': '1',
                        },
                        {
                            'about': '',
                            'CopyrightOwner': {
                                'Seq': {
                                    'li': {
                                        'parseType': 'Resource',
                                        'CopyrightOwnerID': 'Default',
                                        'CopyrightOwnerName': 'Joe Photographer',
                                    }
                                }
                            },
                            'ImageCreator': {
                                'Seq': {
                                    'li': {
                                        'parseType': 'Resource',
                                        'ImageCreatorID': 'Default',
                                        'ImageCreatorName': 'Joe Photographer',
                                    }
                                }
                            },
                            'ImageSupplier': {
                                'Seq': {
                                    'li': {
                                        'parseType': 'Resource',
                                        'ImageSupplierID': 'image supplier id',
                                        'ImageSupplierName': 'image aupplier name',
                                    }
                                }
                            },
                            'ImageSupplierImageID': 'suppliers image id',
                            'MinorModelAgeDisclosure': 'http://ns.useplus.org/ldf/vocab/AG-A25',
                            'ModelReleaseID': {'Bag': {'li': 'model release ids'}},
                            'ModelReleaseStatus': 'http://ns.useplus.org/ldf/vocab/MR-LMR',
                            'PropertyReleaseID': {'Bag': {'li': 'property release ids'}},
                            'PropertyReleaseStatus': 'http://ns.useplus.org/ldf/vocab/PR-UPR',
                        },
                        {
                            'about': '',
                            'CreateDate': '2017-05-29T17:19:21-04:00',
                            'CreatorTool': 'Adobe Photoshop Lightroom 6.10.1 (Macintosh)',
                            'MetadataDate': '2017-07-17T12:17:25-04:00',
                            'ModifyDate': '2017-07-17T12:17:25-04:00',
                            'Rating': '0',
                        },
                        {
                            'about': '',
                            'DocumentID': 'xmp.did:49a1e4c8-d59e-40ec-837f-3718022f9dea',
                            'History': {
                                'Seq': {
                                    'li': [
                                        {
                                            'parseType': 'Resource',
                                            'action': 'derived',
                                            'parameters': 'saved to new location',
                                        },
                                        {
                                            'parseType': 'Resource',
                                            'action': 'derived',
                                            'parameters': 'converted from image/jpeg to image/tiff',
                                        },
                                        {
                                            'parseType': 'Resource',
                                            'action': 'converted',
                                            'parameters': 'from image/tiff to image/jpeg',
                                        },
                                        {
                                            'parseType': 'Resource',
                                            'action': 'derived',
                                            'parameters': 'converted from image/tiff to image/jpeg',
                                        },
                                        {
                                            'parseType': 'Resource',
                                            'action': 'derived',
                                            'parameters': 'saved to new location',
                                        },
                                    ]
                                }
                            },
                            'InstanceID': 'xmp.iid:49a1e4c8-d59e-40ec-837f-3718022f9dea',
                            'OriginalDocumentID': 'C2FF15856CFA5CB554F4CB05B9933A56',
                        },
                        {
                            'about': '',
                            'Marked': 'True',
                            'UsageTerms': {
                                'Alt': {
                                    'li': {
                                        'lang': 'x-default',
                                        'text': 'This image is licensed under Creative Commons 4.0',
                                    }
                                }
                            },
                            'WebStatement': 'metadatamatters.blog',
                        },
                        {
                            'about': '',
                            'AlreadyApplied': 'True',
                            'AutoLateralCA': '0',
                            'AutoWhiteVersion': '134348800',
                            'Blacks2012': '0',
                            'BlueHue': '0',
                            'BlueSaturation': '0',
                            'CameraProfile': 'Embedded',
                            'Clarity2012': '0',
                            'ColorNoiseReduction': '0',
                            'Contrast2012': '0',
                            'ConvertToGrayscale': 'False',
                            'DefringeGreenAmount': '0',
                            'DefringeGreenHueHi': '60',
                            'DefringeGreenHueLo': '40',
                            'DefringePurpleAmount': '0',
                            'DefringePurpleHueHi': '70',
                            'DefringePurpleHueLo': '30',
                            'Dehaze': '0',
                            'Exposure2012': '0.00',
                            'GrainAmount': '0',
                            'GreenHue': '0',
                            'GreenSaturation': '0',
                            'HasSettings': 'True',
                            'Highlights2012': '0',
                            'HueAdjustmentAqua': '0',
                            'HueAdjustmentBlue': '0',
                            'HueAdjustmentGreen': '0',
                            'HueAdjustmentMagenta': '0',
                            'HueAdjustmentOrange': '0',
                            'HueAdjustmentPurple': '0',
                            'HueAdjustmentRed': '0',
                            'HueAdjustmentYellow': '0',
                            'IncrementalTemperature': '0',
                            'IncrementalTint': '0',
                            'LensManualDistortionAmount': '0',
                            'LensProfileEnable': '0',
                            'LensProfileSetup': 'LensDefaults',
                            'LuminanceAdjustmentAqua': '0',
                            'LuminanceAdjustmentBlue': '0',
                            'LuminanceAdjustmentGreen': '0',
                            'LuminanceAdjustmentMagenta': '0',
                            'LuminanceAdjustmentOrange': '0',
                            'LuminanceAdjustmentPurple': '0',
                            'LuminanceAdjustmentRed': '0',
                            'LuminanceAdjustmentYellow': '0',
                            'LuminanceSmoothing': '0',
                            'ParametricDarks': '0',
                            'ParametricHighlightSplit': '75',
                            'ParametricHighlights': '0',
                            'ParametricLights': '0',
                            'ParametricMidtoneSplit': '50',
                            'ParametricShadowSplit': '25',
                            'ParametricShadows': '0',
                            'PerspectiveAspect': '0',
                            'PerspectiveHorizontal': '0',
                            'PerspectiveRotate': '0.0',
                            'PerspectiveScale': '100',
                            'PerspectiveUpright': '0',
                            'PerspectiveVertical': '0',
                            'PerspectiveX': '0.00',
                            'PerspectiveY': '0.00',
                            'PostCropVignetteAmount': '0',
                            'ProcessVersion': '6.7',
                            'RedHue': '0',
                            'RedSaturation': '0',
                            'Saturation': '0',
                            'SaturationAdjustmentAqua': '0',
                            'SaturationAdjustmentBlue': '0',
                            'SaturationAdjustmentGreen': '0',
                            'SaturationAdjustmentMagenta': '0',
                            'SaturationAdjustmentOrange': '0',
                            'SaturationAdjustmentPurple': '0',
                            'SaturationAdjustmentRed': '0',
                            'SaturationAdjustmentYellow': '0',
                            'ShadowTint': '0',
                            'Shadows2012': '0',
                            'SharpenDetail': '25',
                            'SharpenEdgeMasking': '0',
                            'SharpenRadius': '+1.0',
                            'Sharpness': '0',
                            'SplitToningBalance': '0',
                            'SplitToningHighlightHue': '0',
                            'SplitToningHighlightSaturation': '0',
                            'SplitToningShadowHue': '0',
                            'SplitToningShadowSaturation': '0',
                            'ToneCurve': {'Seq': {'li': ['0, 0', '255, 255']}},
                            'ToneCurveBlue': {'Seq': {'li': ['0, 0', '255, 255']}},
                            'ToneCurveGreen': {'Seq': {'li': ['0, 0', '255, 255']}},
                            'ToneCurveName': 'Linear',
                            'ToneCurveName2012': 'Linear',
                            'ToneCurvePV2012': {'Seq': {'li': ['0, 0', '255, 255']}},
                            'ToneCurvePV2012Blue': {'Seq': {'li': ['0, 0', '255, 255']}},
                            'ToneCurvePV2012Green': {'Seq': {'li': ['0, 0', '255, 255']}},
                            'ToneCurvePV2012Red': {'Seq': {'li': ['0, 0', '255, 255']}},
                            'ToneCurveRed': {'Seq': {'li': ['0, 0', '255, 255']}},
                            'ToneMapStrength': '0',
                            'UprightCenterMode': '0',
                            'UprightCenterNormX': '0.5',
                            'UprightCenterNormY': '0.5',
                            'UprightFocalLength35mm': '35',
                            'UprightFocalMode': '0',
                            'UprightFourSegmentsCount': '0',
                            'UprightPreview': 'False',
                            'UprightTransformCount': '6',
                            'UprightVersion': '151388160',
                            'Version': '9.10.1',
                            'Vibrance': '0',
                            'VignetteAmount': '0',
                            'WhiteBalance': 'As Shot',
                            'Whites2012': '0',
                        },
                        {
                            'about': '',
                            'History': 'New Layer\nMake layer\t2\n',
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
                        'Headline': 'President Trump Departs Washington For NATO Summit',
                        'Credit': 'Getty Images',
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
