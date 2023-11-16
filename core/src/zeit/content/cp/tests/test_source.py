from zeit.cms.testing import copy_inherited_functions
import zeit.cms.content.tests.test_contentsource
import zeit.cms.testing
import zeit.content.cp.source
import zeit.content.cp.testing


class CPSourceTest(
    zeit.cms.content.tests.test_contentsource.ContentSourceBase,
    zeit.content.cp.testing.FunctionalTestCase,
):
    source = zeit.content.cp.source.centerPageSource
    expected_types = ['centerpage-2009']

    copy_inherited_functions(zeit.cms.content.tests.test_contentsource.ContentSourceBase, locals())
