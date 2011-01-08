# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""Clean up functions for the cms process."""

import gc
import sys
import zope.app.publication.interfaces
import zope.component
import zope.security.management


# Lower the gc thresholds
gc.set_threshold(700, 10, 5)


@zope.component.adapter(zope.app.publication.interfaces.IEndRequestEvent)
def clean_exc_info(event):
    sys.exc_clear()


@zope.component.adapter(zope.app.publication.interfaces.IEndRequestEvent)
def clean_previous_interaction(event):
    try:
        del zope.security.management.thread_local.previous_interaction
    except AttributeError:
        pass
