from zeit.cms.testing import copy_inherited_functions
import zeit.cms.content.tests.test_contentsource
import zeit.content.portraitbox.testing


class PortraitboxSourceTest(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase,
        zeit.content.portraitbox.testing.FunctionalTestCase):

    source = zeit.content.portraitbox.interfaces.portraitboxSource
    expected_types = ['portraitbox']

    copy_inherited_functions(
        zeit.cms.content.tests.test_contentsource.ContentSourceBase, locals())
