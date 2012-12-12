# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IRepositoryContent
import transaction
import urllib
import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zope.browser.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.formlib.form
import zope.i18n


class WorkflowMenuItem(zeit.cms.browser.menu.ContextViewsMenu):
    """The Workflow menu item which is active when no other item is active."""

    title = _("Workflow")
    sort = -1
    viewURL = "@@workflow.html"
    activeCSS = 'workflow selected'
    inActiveCSS = 'workflow'

    @property
    def selected(self):
        """We are selected when no other item is selected."""
        return self.request.getURL().endswith('@@workflow.html')

    def render(self):
        # XXX kludgy: we don't want to show this menu item for IArticle.
        # To do that, we want to override the viewlet for IArticle,
        # but we can't do that if we register this for IRepositoryContent,
        # since that is orthogonal to the type, while ICMSContent is
        # a superclass of IArticle.
        if not IRepositoryContent.providedBy(self.context):
            return ''
        return super(WorkflowMenuItem, self).render()
