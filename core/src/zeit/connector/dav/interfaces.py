# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import httplib


class DavXmlParseError(Exception):
    """The response from the server could not be parsed."""


class DAVError(Exception):
    """Generic DAV exception"""

    def __init__(self, *args):
        if len(args) == 5:
            self.status, self.reason, self.url, self.body, self.response = (
                args)
        super(DAVError, self).__init__(*args)


class DAVNoFileError(DAVError):
    """Exception raised if a DAVFile specific method is invoked on a collection.
    """


class DAVNoCollectionError(DAVError):
    """Exception raised if a collection specific method is invoked
    on a non-collection.
    """


class DAVNotFoundError(DAVError):
    """Exception raised if a resource or a property was not found.
    """


class DAVLockedError(DAVError):
    """Raised when modifying or locking a locked resource."""


class DAVRedirectError(DAVError):
    """Raised when a resource was moved."""


class PreconditionFailedError(httplib.HTTPException):
    """Raised when a precondition (if header) fails."""


class DAVBadStatusLineError(DAVError):
    """Exception raised when we don't grok a status line

       (that's one of those "HTTP/1.1 200 OK" thingies around there)

       Note: This is different from httplib.BadStatusline as
       DAVBadStatusLineError is raised when there is a bad status line *in* the
       DAV *XML* response.

       """
