# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface


class ITemplateWidgetSetup(zope.interface.Interface):
    """Adapter which sets up widget values from a template."""

    def setup_widget(widgets, session_key, chooser_schema,
                     ignore_request=False):
        """Setup widgets

        widgets: sequence of the widgets to setup
        session_key: to get the template from the session.
        chooser_schema: Schema with the template field.
        ignore_request: nothing done if True

        """


class IXMLTreeWidget(zope.app.form.browser.interfaces.ITextBrowserWidget):
    """A widget for source editing xml trees."""


class IXMLSnippetWidget(zope.app.form.browser.interfaces.ITextBrowserWidget):
    """A widget for editing xml snippets."""


class IAssetViews(zope.interface.Interface):
    """Marker interface for object which want asset views."""
