import dav
from testconf import CONN, URL

###

do = dav.DAVCollection(URL, CONN)

do.update()

try:
    res = do.unlock('opaquelocktoken:1fc30a2a-1dd2-11b2-93f6-f82070511a96')
    print str(res)
except dav.DAVNotLockedError:
    print "not locked!"
## print str(res.msg.headers)
## print str(res.read())
