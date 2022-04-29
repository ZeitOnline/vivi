import zope.component
import zope.interface


class FragmentHarness:

    def render(self):
        view = zope.component.getMultiAdapter(
            (self.context, self.request), zope.interface.Interface,
            name=self.request.get('view'))
        return view()
