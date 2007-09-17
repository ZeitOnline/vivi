#!/usr/bin/env python
"""Tests for pydavclient.

You have to provide a base url which must be WebDAV aware as a parameter.
Example:
  python ./test.py http://localhost/storage/
"""

import sys
import unittest
import urlparse
import getpass

import dav

###

# setup server and path from parameters
_url = sys.argv[1:2]
if not _url:
    sys.stderr.write("""usage: %s url
where url refers to a WebDAV enabled location.
""" % sys.argv[0])
    sys.exit(1)
#
_t = urlparse.urlparse(_url[0])
SCHEME=_t[0].lower()
SERVER=_t[1]
TEST_URL = _url[0]
TEST_PATH=_t[2]
TEST_COLL_URL= urlparse.urlunsplit(_t[:-1])
TEST_FILE_URL= urlparse.urljoin(TEST_COLL_URL, 'testfile')
del _t
del _url
del sys.argv[1]

print
print "Testing on server:", SERVER
print "  Path:", TEST_PATH
print "   URL:", TEST_URL
print "  Collection URL:", TEST_COLL_URL
print "  File URL:", TEST_FILE_URL
print

user = ''
passwd = ''
use_auth=False

warnings = []

###

def get_user_pw ( conn ):
    global use_auth, user, passwd
    u = raw_input('User: ')
    p = getpass.getpass('Password: ')
    conn.set_auth(u,p)
    user, passwd = u, p
    use_auth = True
    return
#
###

class DAVTestBasic ( unittest.TestCase ):

    def setUp ( self ):
        '''Set up the stage for the tests.
        '''
        if SCHEME == 'http':
            self.dconn = dav.DAVConnection(SERVER)
        elif SCHEME == 'https':
            self.dconn = dav.DAVSConnection(SERVER)
        if use_auth:
            self.dconn.set_auth(user, passwd)
        return

    def test_01_Connection ( self ):
        '''Test connection to a WebDAV server using the OPTIONS method.
        Also checks if the WebDAV methods are supported.
        '''
        global warnings
        METHODS = ['PROPFIND', 'PROPPATCH', 'COPY', 'MOVE', 'LOCK', 'UNLOCK', 'DELETE']
        conn = self.dconn
        response = conn.options(TEST_URL)
        if response.status == 401:
            data = response.read()
            get_user_pw(conn)
            response = conn.options(TEST_URL)
        self.failIf(response.status != 200, "Status code %d" % response.status)
        data = response.read()
        if len(data) > 0:
            warnings.append("OPTIONS request returned data of length %d!" % len(data))
        dav = response.msg.getallmatchingheaders('DAV')
        self.failIf( dav is None, "Ooops... the server is not WebDAV aware!\nNo DAV: header was returned!")
        ah = response.msg.getheader('allow', None)
        self.failIf(ah is None, "Request didn't return an Allow header!")
        allowed = [ x.strip() for x in ah.split(',') ]
        for m in METHODS:
            self.failIf( m not in allowed, "Method %s not supported by this server!" % m)
        # ok, consider the connection is fine
        return

    def test_02_DAVResource_01_init ( self ):
        '''Test DAVResource initialization.
        '''
        global warnings
        conn = self.dconn
        do = dav.DAVResource(TEST_COLL_URL, conn)
        do.update()
        self.failIf(do._result is None, "DAVResource not updated properly!")
        allns = do.get_property_namespaces()
        self.failIf( len(allns) < 1, "No property namespaces found!")
        self.failIf( 'DAV:' not in allns, "Couldn't find DAV: namespace!")
        return

    def test_02_DAVResource_02_init_fail ( self ):
        '''Test DAVResource initialization.
        '''
        global warnings
        conn = self.dconn
        try:
            do = dav.DAVResource(TEST_COLL_URL + '/ghghhg/', conn)
            do.update()
            self.fail("Creation of DAVResource should have been rejected!")
        except dav.DAVNotFoundError:
            # expected result
            pass
        return

    def test_03_DAVResource_03_propfind ( self ):
        '''Test DAVResource property reading.
        '''
        global warnings
        conn = self.dconn
        do = dav.DAVResource(TEST_COLL_URL, conn)
        do.update()
        pnames = do.get_property_names()
        self.failIf( len(pnames) < 1, "No properties found!")
        # test for some dead properties in DAV: namespace that must be there
        for p in ['creationdate', 'getlastmodified']:
            try:
                v = do.get_property_value((p, 'DAV:'))
                self.failIf( not v, "No value returned for property %s!" % p)
            except dav.DAVNotFoundError:
                self.fail("Property %s not found!" % p)
                pass
        # test non-existent properties
        pn = ('xxxx', 'AAA:')
        try:
            v = do.get_property_value(pn)
            self.failIf( v, "No error while looking for property %s!" % pn[0])
        except dav.DAVNotFoundError, ex:
            # expected result
            pass
        return

    def test_04_DAVResource_03_prop_set_and_del ( self ):
        '''Test DAVResource set/read/delete properties.
        '''
        global warnings
        conn = self.dconn
        do = dav.DAVResource(TEST_COLL_URL, conn)
        do.update()
        # create a new property on resource
        # use namespace TEST:
        pdict = { ('testx', 'TEST:'): 'test', ('testx', 'TEST2:'): 'test 2' }
        res = do.set_properties(pdict)
        self.failIf( res.status != 207, "Returned status is %d" % res.status)
        # check if properties were created and have the right value
        do.update()
        for pn in pdict.keys():
            try:
                v = do.get_property_value(pn)
                self.failIf( not v, "No value returned for property %s!" % pn[0])
                self.failIf( v != pdict[pn], "Wrong value %s returned instead of %s!" % (v, pdict[pn]))
            except dav.DAVNotFoundError:
                self.fail("Property %s not found!" % pn)
                pass
        # end for
        # change value of existing property
        for k in pdict.keys():
            pdict[k] = 'TEST TEST TEST'
        res = do.set_properties(pdict)
        self.failIf( res.status != 207, "Returned status is %d instaead of 207!" % res.status)
        # check if property was changed and has the right value
        do.update()
        for pn in pdict.keys():
            try:
                v = do.get_property_value(pn)
                self.failIf( not v, "No value returned for property %s!" % pn[0])
                self.failIf( v != pdict[pn], "Wrong value %s returned instead of %s!" % (v, pdict[pn]))
            except dav.DAVNotFoundError:
                self.fail("Property %s not found!" % pn)
                pass
        # delete properties
        res = do.del_properties(pdict.keys())
        self.failIf( res.status != 207, "Returned status is %d instead of 207!" % res.status)
        # check if property was deleted
        do.update()
        for pn in pdict.keys():
            try:
                v = do.get_property_value(pn)
                self.failIf( v, "A value returned for property %s!" % repr(pn))
            except dav.DAVNotFoundError:
                pass
        return

    def test_05_DAVResource_04_lock_unlock ( self ):
        '''Test DAVResource (un-)locking.
        '''
        global warnings
        conn = self.dconn
        do = dav.DAVResource(TEST_COLL_URL, conn)
        do.update()
        # lock this collection w/o owner and depth 0
        locktoken = do.lock(depth=0)
        self.failIf( len(locktoken) < 10, "Strange locktoken received: %s" % locktoken)
        do.update()
        self.failIf( not do.is_locked(), "Resource not locked!")
        lockinfo = do.get_locking_info()
        self.failIf( not lockinfo, "Lockinfo is empty!")
        self.failIf( locktoken != lockinfo['locktoken'], "Locktoken mismatch!")
        # now unlock it again
        do.unlock(locktoken)
        do.update()
        self.failIf( do.is_locked(), "Resource still locked!")
        return
#

class DAV_Test_Collection ( unittest.TestCase ):

    def setUp ( self ):
        '''Set up the stage for the tests.
        '''
        if SCHEME == 'http':
            self.dconn = dav.DAVConnection(SERVER)
        elif SCHEME == 'https':
            self.dconn = dav.DAVSConnection(SERVER)
        if use_auth:
            self.dconn.set_auth(user, passwd)
        return

    def test_01_DAVCollection_01_init ( self ):
        '''Test DAVCollection initialization.
        '''
        conn = self.dconn
        do = dav.DAVCollection(TEST_COLL_URL, conn)
        do.update()
        self.failIf(do._result is None, "DAVFile not updated properly!")
        allns = do.get_property_namespaces()
        self.failIf( len(allns) < 1, "No property namespaces found!")
        self.failIf( 'DAV:' not in allns, "Couldn't find DAV: namespace!")
        return

    def test_02_DAVCollection_01_init_fail ( self ):
        '''Test DAVCollection initialization which should fail.
        '''
        conn = self.dconn
        try:
            do = dav.DAVCollection(TEST_FILE_URL, conn)
            self.fail("URL is not a collection!")
        except dav.DAVNoCollectionError:
            pass
        except dav.DAVNotFoundError:
            pass
        return

    def test_03_DAVCollection_02_children_names ( self ):
        '''Test DAVCollection children names.
        '''
        conn = self.dconn
        do = dav.DAVCollection(TEST_COLL_URL, conn)
        cnames = do.get_child_names()
        self.failIf( len(cnames) < 1, "No children found!")
        return

    def test_04_DAVCollection_02_children_objects ( self ):
        '''Test DAVCollection children names.
        '''
        conn = self.dconn
        do = dav.DAVCollection(TEST_COLL_URL, conn)
        cnames = do.get_child_objects()
        self.failIf( len(cnames) < 1, "No children found!")
        return

    def test_05_DAVCollection_03_create_coll ( self ):
        '''Test DAVCollection creation of collection.
        '''
        conn = self.dconn
        do = dav.DAVCollection(TEST_COLL_URL, conn)
        # create a sub-collection called testdir
        try:
            do2 = do.create_collection('testdir')
            self.failIf( not do2.is_collection(), "Resulting object is not a collection!")
        except dav.DAVNotFoundError:
            self.fail("Resource couldn't be found!")
            raise
        except dav.DAVLockedError:
            self.fail("Resource is locked!")
            raise
        except dav.DAVCreationFailedError, ex:
            self.fail("Creation of testdir failed: %d %s" % ex.args[:2])
            raise
        return

    def test_06_DAVCollection_03_delete_coll ( self ):
        '''Test DAVCollection delete of collection.
        '''
        conn = self.dconn
        do = dav.DAVCollection(TEST_COLL_URL, conn)
        # delete the sub-collection called testdir
        try:
            do.delete('testdir')
            do.update()
            p = TEST_PATH + 'testdir'
            fnames = do.get_child_names()
            self.failIf( p in fnames, "Collection testdir not deleted!")
        except dav.DAVNotFoundError, ex:
            self.fail("Sub-Collection testdir not found!")
            raise
        except dav.DAVLockedError:
            self.fail("Sub-Collection testdir is locked!")
            raise
        return

    def test_07_DAVCollection_04_create_file ( self ):
        '''Test DAVCollection creation of file.
        '''
        conn = self.dconn
        do = dav.DAVCollection(TEST_COLL_URL, conn)
        # create a file called testfile
        try:
            do2 = do.create_file('testfile')
            self.failIf( do2.is_collection(), "Resulting object is a collection!")
        except dav.DAVNotFoundError:
            self.fail("Resource couldn't be found!")
            raise
        except dav.DAVLockedError:
            self.fail("Resource is locked!")
            raise
        except dav.DAVCreationFailedError, ex:
            self.fail("Creation of testfile failed: %d %s" % ex.args[:2])
            raise
        return

    def test_08_DAVCollection_04_delete_file ( self ):
        '''Test DAVCollection delete of file.
        '''
        conn = self.dconn
        do = dav.DAVCollection(TEST_COLL_URL, conn)
        # delete the file called testfile
        try:
            do.delete('testfile')
            do.update()
            p = TEST_PATH + 'testfile'
            fnames = do.get_child_names()
            self.failIf( p in fnames, "File testfile not deleted!")
        except dav.DAVNotFoundError, ex:
            self.fail("File testfile not found!")
            raise
        except dav.DAVLockedError:
            self.fail("File testfile is locked!")
            raise
        return

#

##     def test_02_DAVFile_01_init_fail ( self ):
##         '''Test DAVFile initialization which should fail.
##         '''
##         conn = self.dconn
##         try:
##             do = dav.DAVFile(TEST_COLL_URL, conn)
##             self.fail( "URL points to collection!")
##         except dav.DAVNoFileError:
##             # this is the expected result
##             pass
##         return

##     def test_03_DAVFile_02_propfind ( self ):
##         '''Test DAVFile property find.
##         '''
##         conn = self.dconn
##         do = dav.DAVFile(TEST_FILE_URL, conn)
##         do.update()
##         pnames = do.get_property_names()
##         self.failIf( len(pnames) < 1, "No properties found!")
##         # test for some dead properties in DAV: namespace that must be there
##         for p in ['getcontentlength', 'getlastmodified']:
##             try:
##                 v = do.get_property_value((p, 'DAV:'))
##                 self.failIf( not v, "No value returned for property %s!" % p)
##             except dav.DAVNotFoundError:
##                 self.fail("Property %s not found!" % p)
##                 pass
##         # test non-existent properties
##         pn = ('xxxx', 'AAA:')
##         try:
##             v = do.get_property_value(pn)
##             self.fail("No error while looking for property %s!" % pn)
##         except dav.DAVNotFoundError, ex:
##             # expected result
##             pass
##         return



##     def test_09_DAVFile_01_init ( self ):
##         '''Test DAVFile initialization.
##         '''
##         conn = self.dconn
##         do = dav.DAVFile(TEST_FILE_URL, conn)
##         do.update()
##         self.failIf(do._result is None, "DAVFile not updated properly!")
##         allns = do.get_property_namespaces()
##         self.failIf( len(allns) < 1, "No property namespaces found!")
##         self.failIf( 'DAV:' not in allns, "Couldn't find DAV: namespace!")
##         return

#
###

def suite ():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(DAV_Test_Basic, 'test_'))
    s.addTest(unittest.makeSuite(DAV_Test_Collection, 'test_'))
    return s
#

if '__main__' == __name__:
    unittest.main()
    if warnings:
        print
        print 'Warnings:'
        print '\n'.join(warnings)
        print
#
