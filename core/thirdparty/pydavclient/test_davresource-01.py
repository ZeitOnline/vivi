import dav

from testconf import CONN, URL

###

def print_do ( do ):
    print "DATA FOR:", do.url
    print "Is collection", do.is_collection()
    print
    print "Is locked", do.is_locked()
    print
    print "used namespaces:"
    nss = do.get_property_namespaces()
    for n in nss:
        print "  ", str(n)
    print
    if not do.is_collection():
        fs = do.file_size()
        print "size: %d" % fs
        print
    for ns in nss:
        print "Properties in namespace: %s" % ns
        pns = do.get_property_names(ns)
        for p in pns:
            print p[0]
        print
    print
    if do.is_collection():
        fos = do.get_child_objects()
        for f in fos:
            print_do(f)
            print "-"*40
        print
    return
#
###

do = dav.DAVCollection(URL, CONN)

print_do(do)
