# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.addcentral.interfaces
import zope.interface


class ContentAdder(object):

    zope.interface.implements(zeit.addcentral.interfaces.IContentAdder)

    type_ = None
    ressort = None
    sub_ressort = None
    year = None
    month = None

# def add_content(type_, ressort, subressort, year, month):
#     folder = find_or_create_folder(ressort, subressort, year, month)
#     redirect_to(folder, type_.add_form)
