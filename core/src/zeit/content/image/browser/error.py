# coding: utf8
# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

class ProcessingError(object):

    def __call__(self):
        self.request.response.setStatus(500)
        return self.index()
