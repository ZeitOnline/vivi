// Copyright (c) 2007 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$

function setCookie(name, value, expires, path, domain, secure) {   
    var val = escape(value);
    cookie = name + "=" + val +
	((expires) ? "; expires=" + expires.toGMTString() : "") +
	((path) ? "; path=" + path : "") +
	((domain) ? "; domain=" + domain : "") +
	((secure) ? "; secure" : "");
    document.cookie = cookie;
}

function getCookie(name) {
    	var dc = document.cookie;
    	var prefix = name + "=";
    	var begin = dc.indexOf("; " + prefix);
    	if (begin == -1) {
        	begin = dc.indexOf(prefix);
        	if (begin != 0) return null;
    	} else {
        	begin += 2;
    	}
    	var end = document.cookie.indexOf(";", begin);
    	if (end == -1) {
        	end = dc.length;
    	}
    	return unescape(dc.substring(begin + prefix.length, end));
}

function PanelHandler(base_url) {
    this.url = base_url + '/panel_handlers';
}

PanelHandler.prototype = {

    registerPanelHandlers: function() {
        var panels = getElementsByTagAndClassName('div', 'panel');
        var handler = this;

        forEach(panels, function(panel) {
            var foldmarker = panel.getElementsByTagName('h1')[0];
            connect(foldmarker, "onclick", function(event) {
                if (event.target() != foldmarker) return;
                var new_state;
                if (hasElementClass(panel, 'folded')) {
                    removeElementClass(panel, 'folded');
                    addElementClass(panel, 'unfolded');
                } else {
                    removeElementClass(panel, 'unfolded');
                    addElementClass(panel, 'folded');
                }
                handler.storeState(panel.id);
            });
            var content_element = getFirstElementByTagAndClassName(
                'div', 'PanelContent', panel)
            handler.restoreScrollState(content_element);
            connect(window, 'onunload', function(event) {
                handler.rememberScrollState(content_element);
            });
            connect(content_element, 'initialload', function(event) {
                if (event.src() == content_element) {
                    handler.restoreScrollState(content_element);
                }
            });
        });

    },

    storeState: function(panel_id) {
        doSimpleXMLHttpRequest(this.url, {toggle_folding: panel_id});
    },


    rememberScrollState: function(content_element) {
        var position = content_element.scrollTop;
        var id = content_element.id;
        if (!id) {
            return;
        }
        setCookie(id, position.toString(), null, '/');
     },

    restoreScrollState: function(content_element) {
        var id = content_element.id;
        if (!id) {
            return;
        }
        var position = getCookie(id);
        content_element.scrollTop = position;
    },
};



// Handler to close and open the sidebar making more space for the actual
// content area.

function SidebarDragger(base_url) {
    this.url = base_url + '/@@sidebar_toggle_folding';
    this.sidebar = getElement('sidebar');
    this.dragger = getElement('sidebar-dragger')
    this.content = getElement('content');

}

SidebarDragger.prototype = {

    classes: ['sidebar-folded', 'sidebar-expanded'],
    
    toggle: function(event) {
        var dragger = this;
        var d = doSimpleXMLHttpRequest(this.url);
        d.addCallback(function(result) {
            var css_class = result.responseText;
            dragger.setClass(css_class);
        });
    },

    setClass: function(css_class) {
        var dragger = this;
        forEach([this.sidebar, this.dragger, this.content], function(element) {
            forEach(dragger.classes, function(cls) {
                removeElementClass(element, cls);
                });
        addElementClass(element, css_class);
        });
    },
}

