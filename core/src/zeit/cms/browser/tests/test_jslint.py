# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.jslint


class JSLintTest(gocept.jslint.TestCase):

    include = ('zeit.cms.browser:js',)
    exclude = (
        'MochiKit.js',
        'json-template.js',
        )

    options = (gocept.jslint.TestCase.options +
               ('--eqeq',
                '--evil',
                '--forin',
                '--plusplus',
                '--predef='
                'zeit,gocept,application_url,context_url,'
                'jQuery,DOMParser,'
                'console,'
                'alert,confirm,escape,unescape,'
                'jsontemplate,'
                'MochiKit,$,forEach,filter,map,'
                'log,repr,logger,logDebug,logError,' # XXX
                'DIV,A,UL,LI,INPUT,'
                'isNull,isUndefined,isUndefinedOrNull',
                ))

    ignore = (
        "Avoid 'arguments.callee'",
        "Do not use 'new' for side effects",
        "Don't make functions within a loop",
        "Expected an identifier and instead saw 'import'",
        "Use a named parameter",
        )
