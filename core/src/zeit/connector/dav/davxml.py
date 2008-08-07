# TODO:
# - maybe change parsing to use an explicit parser object with etree.XMLParser(ns_clean=True)?

__all__ = ('xml_from_string', 'xml_from_file' )

import lxml
from StringIO import StringIO


class DavXmlParseError ( Exception ):
    pass


class _DavXmlDoc:

    def __init__ ( self ):
        self.doc   = None
        self.ctx   = None
        self.nsmap = { 'D':'DAV:', 'd':'DAV:', 'DAV:' : 'DAV:' }
        return

    def from_string ( self, string ):
        try:
            doc = lxml.etree.fromstring(string)
        except lxml.etree.XMLSyntaxError, e:
            open('/tmp/error.xml', 'w').write(string)
            raise DavXmlParseError, e.error_log.filter_levels(
                lxml.etree.ErrorLevels.FATAL)
        self.doc = doc
        #:fixme: how to handle xpath context generation?
        return

    def from_file ( self, fname ):
        try:
            doc = lxml.etree.parse(fname)
        except lxml.etree.XMLSyntaxError, e:
            raise DavXmlParseError, e.error_log.filter_levels(
                lxml.etree.ErrorLevels.FATAL)
        self.doc = doc
        return

    def xpathEval ( self, expr):
        return self.doc.xpath(expr, namespaces=self.nsmap);

    #:note: why is this here? Or better, iff this is here,
    # why aren't the other node-finding functions here?
    def get_response_nodes ( self ):
        """Return a list of all D:response nodes"""
        res = self.xpathEval('D:response')
        return res

    def get_property_nodes ( self, root ):
        return self.xpathEval('DAV:propstat/DAV:prop/*')


def xml_from_string( data ):
    d = _DavXmlDoc()
    d.from_string(data)
    return d


def xml_from_file ( f_in ):
    d = _DavXmlDoc()
    d.from_file(f_in)
    return d
