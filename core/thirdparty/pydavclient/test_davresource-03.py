import dav

from testconf import CONN, URL

###

do = dav.DAVCollection(URL, CONN)

do.update()

pl = [ ('testx', 'EXT:') ]
res = do.del_properties (pl)

res.dump()
