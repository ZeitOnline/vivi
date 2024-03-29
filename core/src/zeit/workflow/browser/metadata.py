import zope.cachedescriptors.property
import zope.component
import zope.viewlet.viewlet

import zeit.workflow.interfaces


class WorkflowPreview(zope.viewlet.viewlet.ViewletBase):
    fields = zope.formlib.form.FormFields(zeit.workflow.interfaces.IContentWorkflow)

    widgets = None

    def update(self):
        if self.workflow is not None:
            self.widgets = zope.formlib.form.setUpEditWidgets(
                self.fields, 'workflow', self.workflow, self.request, for_display=True
            )

    def render(self):
        if not self.widgets:
            return ''
        return super().render()

    @zope.cachedescriptors.property.Lazy
    def workflow(self):
        return zeit.workflow.interfaces.IContentWorkflow(self.context, None)
