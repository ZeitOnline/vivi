# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Object selector."""

import json
import zope.component
import zeit.cms.content.interfaces


class Selector(object):

    @property
    def initial_query(self):
        source_name = self.request.get('type_filter')
        result = {}
        if source_name:
            source = zope.component.getUtility(
                zeit.cms.content.interfaces.ICMSContentSource,
                name=source_name)
            result['types:list'] = source.get_check_types()
        return json.dumps(result)
