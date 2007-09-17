import dav

from testconf import CONN, URL

###

do = dav.DAVCollection(URL, CONN)

tdict = { ('testx', 'EXT:'): 'xx' }
##           ('creationdate', 'DAV:'): 'dhdhdhdhdhd' }

res = do.set_properties ( tdict )

if res.has_errors():
    print "Errors in result!"
    print
else:
    pass
res.dump()
