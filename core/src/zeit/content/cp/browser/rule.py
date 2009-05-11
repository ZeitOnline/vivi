# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.interfaces


def validate(context):
    validator = zeit.content.cp.interfaces.IValidator(context)
    css_class = ''
    if validator.status:
        css_class = 'validation-%s' % validator.status
    return (css_class, '\n'.join(validator.messages))
