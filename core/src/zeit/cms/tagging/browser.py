# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

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

    grokcore.component.adapts(
        zope.schema.interfaces.ITuple,
        zeit.cms.tagging.interfaces.ITagsForContent,
        zeit.cms.browser.interfaces.ICMSLayer)
    grokcore.component.provides(
        zope.formlib.interfaces.IInputWidget)

    def __call__(self):
        """See IBrowserWidget."""
        value = self._getFormValue()
        contents = []

        contents.append(self._div('update', 'Update tags'))
        contents.append(self._div('value', self.renderValue(value)))
        contents.append(self._emptyMarker())
        contents.append(('<script type="text/javascript">'
                        'MochiKit.Sortable.create("{0}")'
                        '</script').format(self.name))

        return self._div(self.cssClass, "\n".join(contents))

    def renderValue(self, value):
        rendered_items = self.renderItems(value)
        return u'<ol id={1}>{0}</ol>'.format(
            ''.join(rendered_items),
            xml.sax.saxutils.quoteattr(self.name))

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
            dict(code=tag.code, label=tag.label)
            for tag in tagger.values()])
