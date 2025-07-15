from typing import List, Tuple

import zope.interface

from zeit.cms.content.interfaces import IKPI
from zeit.cms.interfaces import ICMSContent


class IKPIDatasource(zope.interface.Interface):
    def query(contents: List[ICMSContent]) -> List[Tuple[ICMSContent, IKPI]]:
        pass


class IKPIUpdateEvent(zope.interface.Interface):
    data = zope.interface.Attribute('')  # List[Tuple[ICMSContent, IKPI]]


@zope.interface.implementer(IKPIUpdateEvent)
class KPIUpdateEvent:
    def __init__(self, data):
        self.data = data
