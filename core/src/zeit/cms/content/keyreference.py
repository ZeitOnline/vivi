from functools import total_ordering


@total_ordering
class CMSContentKeyReference:  # BBB keep until zeit.objectlog generation 2 ran
    def __init__(self, uniqueId):
        self.referenced_object = uniqueId

    def __hash__(self):
        return hash(self.referenced_object)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.referenced_object == other.referenced_object
        if isinstance(other, str):
            return self.referenced_object == other
        return False

    def __gt__(self, other):
        if isinstance(other, type(self)):
            return self.referenced_object > other.referenced_object
        if isinstance(other, str):
            return self.referenced_object > other
        return NotImplemented
