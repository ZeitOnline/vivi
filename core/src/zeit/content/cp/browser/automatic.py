import zeit.content.cp.interfaces


class Display(object):

    def values(self):
        return zeit.content.cp.interfaces.IAutomaticRegion(
            self.context).values()
