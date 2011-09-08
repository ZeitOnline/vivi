# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import cgi
import zeit.content.cp.interfaces


def validate(context):
    validator = zeit.content.cp.interfaces.IValidator(context)
    if validator.status:
        css_class = 'validation-%s' % validator.status
        messages = '\n'.join(validator.messages)
        messages = cgi.escape(messages)
    else:
        css_class = ''
        messages = ''
    return (css_class, messages)
