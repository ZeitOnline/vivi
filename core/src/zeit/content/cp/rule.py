# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt


ERROR = 'error'
WARNING = 'warning'


class NotApplicableException(Exception):
    pass


class Rule(object):
    def __init__(self, code):
        code = '\n'.join([line.strip() for line in code.split('\n')])
        self.code = compile(code, '<string>', 'exec')
        self.status = None
        self.message = None

    def apply(self, context):
        globs = {}
        globs['applicable'] = self.applicable
        globs['message'] = self.set_message
        globs['error_if'] = self.error_if
        globs['error_unless'] = self.error_unless
        globs['warning_if'] = self.warning_if
        globs['warning_unless'] = self.warning_unless
        try:
            eval(self.code, globs)
        except NotApplicableException:
            pass
        return self.status

    def applicable(self, condition):
        if not condition:
            raise NotApplicableException

    def error_if(self, condition):
        if condition:
            self.status = ERROR

    def error_unless(self, condition):
        self.error_if(not condition)

    def warning_if(self, condition):
        if condition:
            self.status = WARNING

    def warning_unless(self, condition):
        self.warning_if(not condition)

    def set_message(self, message):
        self.message = message
