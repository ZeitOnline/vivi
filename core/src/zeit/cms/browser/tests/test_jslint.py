# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.jslint


class JSLintTest(gocept.jslint.TestCase):

    level = 3

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
                'alert,confirm,'
                'jsontemplate,'
                'MochiKit,$,forEach,filter,map,'
                'log,repr,logger,logDebug,logError,' # XXX
                'DIV,A,UL,LI,INPUT,'
                'isNull,isUndefined,isUndefinedOrNull',
                ))
