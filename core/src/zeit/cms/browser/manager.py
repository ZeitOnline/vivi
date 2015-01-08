import zope.viewlet.manager


class SortingViewletManager(zope.viewlet.manager.ViewletManagerBase):

    def sort(self, viewlets):
        return sorted(viewlets)
