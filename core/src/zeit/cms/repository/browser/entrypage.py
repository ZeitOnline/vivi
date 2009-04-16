# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.repository.interfaces
import zope.component


class EntryPage(object):

    def __call__(self):
        repository = self.context['repository']
        url = zope.component.getMultiAdapter(
            (repository, self.request), name='absolute_url')()
        return self.request.response.redirect(url)
