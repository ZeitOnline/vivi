import zeit.content.cp.interfaces


class Display(object):

    def values(self):
        return zeit.content.cp.interfaces.IAutomaticArea(
            self.context).values()
