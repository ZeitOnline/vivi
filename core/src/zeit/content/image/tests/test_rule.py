from zeit.content.image.testing import create_local_image
from zeit.edit.interfaces import IRuleGlobs
from zeit.edit.rule import Rule
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.image.imagegroup
import zeit.content.image.testing
import zeit.edit.tests.fixture


class RuleTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def setUp(self):
        super(RuleTest, self).setUp()
        self.repository['group'] = zeit.content.image.imagegroup.ImageGroup()
        self.group = self.repository['group']

    def test_imagegroup_is_only_applicable_for_IImageGroup(self):
        r = Rule("""
applicable(imagegroup)
error_if(True, u'Context is an ImageGroup')
""")
        # applicable for image group
        s = r.apply(self.group, IRuleGlobs(self.group))
        self.assertEquals(zeit.edit.rule.ERROR, s.status)

        # not applicable for image
        self.repository['group']['group-120x120.jpg'] = create_local_image(
            'new-hampshire-artikel.jpg')
        s = r.apply(
            self.group['group-120x120.jpg'],
            IRuleGlobs(self.group['group-120x120.jpg']))
        self.assertNotEquals(zeit.edit.rule.ERROR, s.status)

    def test_gives_error_if_required_image_scale_is_missing(self):
        r = Rule("""
applicable(imagegroup)
error_if('120x120' not in provided_scales, u'Scale 120x120 is missing')
""")
        s = r.apply(  # error since scale is missing
            self.group, IRuleGlobs(self.group))
        self.assertEquals(zeit.edit.rule.ERROR, s.status)

        self.repository['group']['group-120x120.jpg'] = create_local_image(
            'new-hampshire-artikel.jpg')
        s = r.apply(  # added scale, no error anymore
            self.group, IRuleGlobs(self.group))
        self.assertNotEquals(zeit.edit.rule.ERROR, s.status)
