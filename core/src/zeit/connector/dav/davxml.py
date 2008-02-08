# TODO:
# - maybe change parsing to use an explicit parser object with etree.XMLParser(ns_clean=True)?

__all__ = ('xml_from_string', 'xml_from_file' )

from lxml import etree
from StringIO import StringIO
# from debug import OUT

class _ErrorHandler ( object ):

    def __init__ ( self ):
        self._msgs = []
        self._do_print = False
        return

    def __call__ ( self, first, second ):
        if self._do_print:
            print second
        else:
            self._msgs.append(second)
        return

    def reset ( self ):
        self._msgs = []
        return

    def get_message ( self ):
        return ''.join(self._msgs)

    def set_print ( self, flag ):
        self._do_print = bool(flag)
        return

    def print_message ( self ):
        print self.get_messages()
        return
#
###

#:comment: Do we need this 
#:oldcode: _error_handler = _ErrorHandler()

#:comment: How can we mimic this with lxml
#:oldcode: libxml2.registerErrorHandler(_error_handler, None)

###

class DavXmlParseError ( Exception ):
    pass
#
###

class _XpathContext ( object ):

    def __init__ ( self, doc ):
        self.doc = doc
        self.nsmap = { 'D':'DAV:', 'd':'DAV:' }
        self.ctx = None
        return

    #:comment: does nothing but initialize the namespace map
    #          of the XPath context.
    
    def init ( self ):
        if self.ctx is not None:
            return
        self.ctx = self.doc.xpathNewContext()
        for k, v in self.nsmap.items():
            self.add_namespace(k, v)
        return

    #:comment: frees the XPath context
    def free ( self ):
        self.ctx.xpathFreeContext()
        return

    #:comment: add a namespace to the NS->prefix mapping and
    #          refresh the namespace map.            
    def add_namespace ( self, prefix, uri ):
        if self.ctx is None:
            self.init()
        self.nsmap[prefix] = uri
        self.ctx.xpathRegisterNs(prefix, uri)
        return

    #:comment: evalute an XPath expressinon on the document
    # FIXME: what happens if self.doc is not yet initialized?
    def evaluate ( self, expr, root=None ):
        if self.ctx is None:
            self.init()
        c = self.ctx
        if root is None:
            root = self.doc
        c.setContextNode(root)
        res = c.xpathEval(expr)
        return res
#
###

class _DavXmlDoc:

    def __init__ ( self ):
        self.doc   = None
        self.ctx   = None
        self.nsmap = { 'D':'DAV:', 'd':'DAV:', 'DAV:' : 'DAV:' }
        return

    #:old:
    #:comment: parse data::string and create
    #          a document.
    def from_string ( self, data ):
        global _error_handler
        _error_handler.reset()
        try:
            doc = libxml2.parseDoc(data)
        except libxml2.parserError, ex:
            m = _error_handler.get_message()
            raise DavXmlParseError, m
        self.doc = doc
        self.ctx = _XpathContext(self.doc)
        return

    #:new:
    def from_string ( self, string ):
        #:fixme: add error handling here!
        etree.clearErrorLog()
        try:
            doc = etree.parse(StringIO(string))
        except etree.XMLSyntaxError, e:
            raise DavXmlParseError, e.error_log.filter_levels(etree.ErrorLevels.FATAL)
        self.doc = doc
        #:fixme: how to handle xpath context generation?
        return

    #:old:
    #:comment: parse fname::filename and create
    #          a document.
    def from_file ( self, fname ):
        global _error_handler
        _error_handler.reset()
        try:
            doc = libxml2.parseFile(fname)
        except libxml2.parserError, ex:
            m = _error_handler.get_message()
            raise DavXmlParseError, m
        self.doc = doc
        self.ctx = _XpathContext(self.doc)
        return

    #:new:
    def from_file ( self, fname ):
        #:fixme: add error handling here!
        etree.clearErrorLog()
        try:
            doc = etree.parse(fname)
        except etree.XMLSyntaxError, e:
            raise DavXmlParseError, e.error_log.filter_levels(etree.ErrorLevels.FATAL)
        self.doc = doc
        #:fixme: how to handle xpath context generation?
        return
    
    #:comment: free both document and XPath context
    def free ( self ):
        self.ctx.free()
        self.ctx = None
        self.doc.freeDoc()
        self.doc = None
        return

    #:old:
    #:comment: evaluate an XPath expression
    #:fixme: Semantics anybody? Why on earth the
    #        brittle string-append? LibXML understands
    #        context nodes.

    #:new:
    def xpathEval ( self, expr):
        return self.doc.xpath(expr, namespaces=self.nsmap);

    #:old:
    #:comment: what are the semantics here? Iff fnc returns
    #          a non-nil value walkin stops???
    #:comment: seems to be dead code!
    def xpathMapFunction ( self, expr, fnc ):
        for n in self.ctx.evaluate(expr):
            if fnc(n):
                break
        return

    #:new:
    def xpathMapFunction ( self, expr, fnc ):
        for n in self.xpathEval(expr):
            if fnc(n):
                break
        return

    #:new:
    #:note: why is this here? Or better, iff this is here,
    # why aren't the other node-finding functions here?
    def get_response_nodes ( self ):
        """Return a list of all D:response nodes"""
        res = self.xpathEval('D:response')
        return res

    #:old:
    def get_property_nodes ( self, root ):
        p = root.nodePath() + '/D:propstat/D:prop/*'
        return self.ctx.evaluate(p)

        #:new:
    def get_property_nodes ( self, root ):
        return self.xpathEval('DAV:propstat/DAV:prop/*')
#
###

def xml_from_string( data ):
    d = _DavXmlDoc()
    d.from_string(data)
    return d
#

def xml_from_file ( f_in ):
    d = _DavXmlDoc()
    d.from_file(f_in)
    return d
#
