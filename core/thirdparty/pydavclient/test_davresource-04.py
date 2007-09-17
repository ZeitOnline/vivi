import dav
from testconf import CONN, URL

###

url = URL

## do = dav.DAVCollection(URL, CONN)
## do = dav.DAVFile(URL+'/xxxx', CONN)
do = dav.DAVResource(url, CONN)
## do.update()

print "locking %s" % url

try:
    locktoken = do.lock(owner='<DAV:href>gst</DAV:href>')
    print locktoken
    do.update()
    print "unlocking %s" % url
    res = do.unlock(locktoken)
except dav.DAVLockedError:
    print "is locked!"
    pass
except dav.DAVError, ex:
    print "OOOOOOOOOOOOOOOOO"
    print str(ex)
    pass
except dav.DAVLockFailedError, ex:
    print "FAILED!"
    print str(ex)
    pass
#

