# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zc.resourcelibrary
import grokcore.component
import xml.sax.saxutils
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.tagging.interfaces
import zope.formlib.interfaces
import zope.formlib.source
import zope.schema.interfaces


class Widget(grokcore.component.MultiAdapter,
             zope.formlib.source.SourceMultiCheckBoxWidget):
    """Widget to edit tags on context.

    - "Update" link uses an tagging mechanism to add tags to content
    - The user can sort and (de-)activate tags, but not manually add them.

    """

    grokcore.component.adapts(
        zope.schema.interfaces.ITuple,
        zeit.cms.tagging.interfaces.ITagsForContent,
        zeit.cms.browser.interfaces.ICMSLayer)
    grokcore.component.provides(
        zope.formlib.interfaces.IInputWidget)

    def __call__(self):
        """See IBrowserWidget."""
        zc.resourcelibrary.need('zeit.cms.tagger')
        value = self._getFormValue()
        contents = []

        contents.append(self._div(
            'update', '<a href="#update_tags">Update tags</a>',
            id="{0}.update".format(self.name)))
        contents.append(self._div('value', self.renderValue(value)))
        contents.append(self._emptyMarker())
        contents.append(('<script type="text/javascript">'
                         'new zeit.cms.tagging.Widget("{0}");'
                        '</script>').format(self.name))

        return self._div(self.cssClass, "\n".join(contents), id=self.name)

    def renderValue(self, value):
        rendered_items = self.renderItems(value)
        return u'<ol id={1}>{0}</ol>'.format(
            ''.join(rendered_items),
            xml.sax.saxutils.quoteattr(self.name + ".list"))

    def _renderItem(self, index, text, value, name, cssClass, checked=False):
        """Render an item of the list."""
        return u'<li>{0}</li>'.format(
            super(Widget, self)._renderItem(
                index, text, value, name, cssClass, checked=checked))


class UpdateTags(zeit.cms.browser.view.JSON):

    def json(self):
        tagger = zeit.cms.tagging.interfaces.ITagger(self.context)
        tagger.update()
        return dict(tags=[
            dict(code=tag.code,
                 label=tag.label)
            for tag in tagger.values()])
