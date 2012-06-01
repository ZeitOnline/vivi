# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import json
import zeit.cms.content.sources


class BannerRules(object):

    def __call__(self):
        return json.dumps(list(zeit.cms.content.sources.BannerSource()))
