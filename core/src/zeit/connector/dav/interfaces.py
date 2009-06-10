# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

class DavXmlParseError(Exception):
    """The response from the server could not be parsed."""

class DAVError ( Exception ):
    """Generic DAV exception
    """


class DAVNoFileError ( DAVError ):
    """Exception raised if a DAVFile specific method is invoked on a collection.
    """


class DAVNoCollectionError ( DAVError ):
    """Exception raised if a collection specific method is invoked on a non-collection.
    """


class DAVNotFoundError ( DAVError ):
    """Exception raised if a resource or a property was not found.
    """


class DAVNotConnectedError ( DAVError ):
    """Exception raised if there is no connection to the server.
    """


class DAVLockFailedError ( DAVError ):
    """Exception raised if an attempt to lock a resource failed.
    """


class DAVUnlockFailedError ( DAVError ):
    """Exception raised if an attempt to lock a resource failed.
    """


class DAVLockedError ( DAVError ):
    """Exception raised if an atempt to modify or lock a locked resource was
    made.
    """
    #:fixme: Maybe we should report information about the lock status as well ...


class DAVNotLockedError ( DAVError ):
    """Exception raised if an atempt to unlock a not locked resource was made.
    """
    #:fixme: Maybe we should report information about the lock status as well ...


class DAVNotOwnerError ( DAVError ):
    """Exception raised if an atempt to unlock a resource not owned was made.
    """
    #:fixme: Maybe we should report information about the lock status as well ...


class DAVInvalidLocktokenError ( DAVError ):
    """Exception raised if an attempt to unlock a not locked resource was made.
    """


class DAVCreationFailedError ( DAVError ):
    """Exception raised if an atempt to create a resource failed.
    """


class DAVUploadFailedError ( DAVError ):
    """Exception raised if an atempt to create a resource failed.
    """


class DAVDeleteFailedError ( DAVError ):
    """Exception raised if an atempt to create a resource failed.
    """


class DAVBadStatusLineError ( DAVError ):
    """Exception raised when we don't grok a status line
       (that's one of those "HTTP/1.1 200 OK" thingies around there)
    """
