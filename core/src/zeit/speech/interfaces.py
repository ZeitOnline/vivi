import zope.interface


class ISpeech(zope.interface.Interface):
    def update(self, data: dict):
        """Update audio object"""

    def delete(self, data: dict):
        """Delete audio object"""
