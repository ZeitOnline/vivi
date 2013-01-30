# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.tagging.interfaces import KEYWORD_CONFIGURATION
import grokcore.component
import json
import xml.sax.saxutils
import zc.resourcelibrary
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.tagging.interfaces
import zope.formlib.interfaces
import zope.formlib.itemswidgets
import zope.formlib.source
import zope.formlib.widget
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

    show_helptext = False

    def __call__(self):
        # adapted from zope.formlib.itemswidgets.ItemsEditWidgetBase to
        # - Add update button
        # - Add id and extra css class to our outer div
        value = self._getFormValue()
        contents = []

        contents.append(self._div('value', self.renderValue(value)))
        contents.append(self._div(
            'update', '<a class="button" href="#update_tags">%s</a>'
            % xml.sax.saxutils.escape(self.translate(_('Update tags'))),
            id="%s.update" % self.name))
        contents.append(self._emptyMarker())
        if self.show_helptext:
            contents.append(self._div(
                'help', self.translate(
                _('Only the first ${keywords_shown} keywords'
                  ' are shown with the article.', mapping=dict(
                keywords_shown=KEYWORD_CONFIGURATION.keywords_shown)))))

        return self._div(
            self.cssClass + ' keyword-widget',
            "\n".join(contents), id=self.name)

    def renderValue(self, value):
        zc.resourcelibrary.need('zeit.cms.tagger')
        list_container = u'<ol id={0}></ol>'.format(
            xml.sax.saxutils.quoteattr(self.name + ".list"))
        javascript = """\
<script type="text/javascript">
 var widget = new zeit.cms.tagging.Widget(
 "{name}", {keywords_shown}, {tags});
</script>
""".format(
name=self.name,
keywords_shown=KEYWORD_CONFIGURATION.keywords_shown,
tags=json.dumps(self.renderItems(value)),
        )
        return list_container + javascript

    def _renderItem(self, index, text, value, name, cssClass, checked=False):
        """Render an item of the list."""
        return dict(code=value, label=text)


class UpdateTags(zeit.cms.browser.view.JSON):

    def json(self):
        tagger = zeit.cms.tagging.interfaces.ITagger(self.context)
        tagger.update()
        return dict(tags=[
            dict(code=tag.code,
                 label=tag.label)
            for tag in tagger.values()])


class DisplayWidget(grokcore.component.MultiAdapter,
                    zope.formlib.itemswidgets.ListDisplayWidget):

    grokcore.component.adapts(
        zope.schema.interfaces.ITuple,
        zeit.cms.tagging.interfaces.ITagsForContent,
        zeit.cms.browser.interfaces.ICMSLayer)
    grokcore.component.provides(
        zope.formlib.interfaces.IDisplayWidget)

    def __init__(self, field, source, request):
        super(DisplayWidget, self).__init__(
            field,
            zope.formlib.source.IterableSourceVocabulary(source, request),
            request)

    def __call__(self):
        return zope.formlib.widget.renderElement(
            'div',
            cssClass='keyword-widget',
            contents=super(DisplayWidget, self).__call__(),
            id=self.name)

    def renderItems(self, value):
        """Render items of sequence."""
        # XXX blame formlib for having to copy this method
        items = []
        cssClass = self.cssClass or ''
        if cssClass:
            cssClass += "-item"
        cssClass += ' shown'
        tag = self.itemTag
        for index, item in enumerate(value):
            if index >= KEYWORD_CONFIGURATION.keywords_shown:
                continue
            term = self.vocabulary.getTerm(item)
            items.append(zope.formlib.widget.renderElement(
                tag,
                cssClass=cssClass,
                contents=xml.sax.saxutils.escape(self.textForValue(term))))
        return items
