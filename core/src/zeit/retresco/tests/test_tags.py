import lxml.etree
import zeit.retresco.testing


class TestTags(zeit.retresco.testing.FunctionalTestCase,
               zeit.retresco.testing.TagTestHelpers):
    """Tests zeit.cms.tagging.tag.Tags using zeit.retresco.tagger.Tagger"""

    def setUp(self):
        from zeit.cms.tagging.tag import Tags
        from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
        super().setUp()

        class Content(ExampleContentType):
            tags = Tags()
        self.content = Content()

    def test_read_and_write_values_to_tagger_does_not_change_intrafind_keyword(
            self):
        """Ensure bw-compat for Intrafind keywords on checkin/checkout."""
        from zeit.retresco.tagger import Tagger
        self.set_tags(self.content, """
<tag uuid="uid-karenduve" url_value="karenduve" type="author">Karen Duve</tag>
""")
        self.content.tags = self.content.tags
        self.assertEqual("""\
<rankedTags xmlns:ns="http://namespaces.zeit.de/CMS/tagging">\
<tag uuid="uid-karenduve" url_value="karenduve" type="author">Karen Duve</tag>\
</rankedTags>""", lxml.etree.tostring(Tagger(self.content).to_xml(),
                                      encoding=str))
