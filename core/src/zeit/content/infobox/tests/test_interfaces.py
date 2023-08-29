from zeit.cms.testing import copy_inherited_functions
import zeit.cms.content.tests.test_contentsource
import zeit.content.infobox.interfaces
import zeit.content.infobox.testing


class InfoboxSourceTest(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase,
        zeit.content.infobox.testing.FunctionalTestCase):

    source = zeit.content.infobox.interfaces.infoboxSource
    expected_types = ['infobox']

    copy_inherited_functions(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase, locals())
