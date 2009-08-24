# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import zeit.content.cp.interfaces
import zeit.workflow.dependency
import zeit.workflow.interfaces


class DependentContent(grokcore.component.Adapter):

    grokcore.component.implements(
        zeit.workflow.interfaces.IPublicationDependencies)
    grokcore.component.context(
        zeit.content.cp.interfaces.ICenterPage)
    grokcore.component.name('zeit.content.cp.CenterPage')

    def get_dependencies(self):
        result = []
        for content in zeit.content.cp.interfaces.ICMSContentIterable(
            self.context):
            if zeit.workflow.dependency.has_only_non_semantic_changes(
                content):
                result.append(content)
        return result


class DependentTeasers(grokcore.component.Adapter):

    grokcore.component.implements(
        zeit.workflow.interfaces.IPublicationDependencies)
    grokcore.component.context(
        zeit.content.cp.interfaces.ICenterPage)
    grokcore.component.name('zeit.content.cp.Teaser')

    def get_dependencies(self):
        result = []
        for content in zeit.content.cp.interfaces.ICMSContentIterable(
            self.context):
            if zeit.content.cp.interfaces.ITeaser.providedBy(content):
                result.append(content)
        return result
