import dav
from testconf import CONN, URL

###

do = dav.DAVCollection(URL, CONN)
print do.url

do.update()

d = do.options()
print str(d)


