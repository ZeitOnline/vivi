import zope.interface


class IExtractReferences(zope.interface.Interface):
    def __call__(self):
        """Returns a list of dict {'target': ICMSContent, 'type': str}"""
