import json
import os
import tempfile

import gocept.jslint


class JSLintTestCase(gocept.jslint.TestCase):
    jshint_command = os.environ.get('JSHINT_COMMAND', '/bin/true')

    options = {
        'esversion': '6',
        'evil': True,
        'eqnull': True,
        'multistr': True,
        'sub': True,
        'undef': True,
        'browser': True,
        'jquery': True,
        'devel': True,
    }
    predefined = (
        'zeit',
        'gocept',
        'application_url',
        'context_url',
        'DOMParser',
        'escape',
        'unescape',
        'jsontemplate',
        'MochiKit',
        '$$',
        'forEach',
        'filter',
        'map',
        'extend',
        'bind',
        'log',
        'repr',
        'logger',
        'logDebug',
        'logError',  # XXX
        'DIV',
        'A',
        'UL',
        'LI',
        'INPUT',
        'IMG',
        'SELECT',
        'OPTION',
        'BUTTON',
        'SPAN',
        'LABEL',
        'isNull',
        'isUndefined',
        'isUndefinedOrNull',
        'Uri',
        '_',  # js.underscore
    )

    ignore = (
        'Functions declared within loops',
        "Expected an identifier and instead saw 'import'",
        "Use '===' to compare with",
        "Use '!==' to compare with",
        'Missing radix parameter',
        'Misleading line break',
        'Expected an assignment or function call and instead saw an expression',
    )

    def _write_config_file(self):
        """Copy&paste from baseclass, so we can use non-boolean options."""
        settings = self.options.copy()
        predefined = settings['predef'] = []
        for name in self.predefined:
            predefined.append(name)

        handle, filename = tempfile.mkstemp()
        output = open(filename, 'w')
        json.dump(settings, output)
        output.close()

        return filename
