// Copyright (c) 2011 gocept gmbh & co. kg
// See also LICENSE.txt


function Tree(base_url, element_id) {
    this.base_url = base_url;
    this.contentElement = MochiKit.DOM.getElement(element_id);
    this.event = MochiKit.Signal.connect(
        this.contentElement, 'onclick', this, 'clickHandler');
    this.query_arguments = {};
}


Tree.prototype = {

    destruct: function() {
        MochiKit.Signal.disconnect(this.event);
    },

    clickHandler: function(event) {
        var target = event.target();
        var action = target.getAttribute('action');
        if (action == null) {
            return;
        }

        var d = this.changeState(target, action);
        if (d != null) {
            event.stop();  // event is handled
        }
    },

    changeState: function(node, action) {
        var self = this;
        var uniqueId = node.getAttribute('uniqueId');
        if (uniqueId == null) {
            return null;
        }
        var url = this.base_url + '/@@' + action + 'Tree' ;
        var query = {'uniqueId': uniqueId,
                     'view_url': window.location.href};
        MochiKit.Base.update(query, this.query_arguments);
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url, query);
        MochiKit.DOM.addElementClass(self.contentElement, 'busy');
        d.addCallback(
            function(result) {
                self.replaceTree(result.responseText);
                MochiKit.Signal.signal(self, 'state-changed');
                return result;
            });
        d.addErrback(function(error) {
            zeit.cms.log_error(error);
            return error;
        });
        d.addBoth(function(result) {
            MochiKit.DOM.removeElementClass(self.contentElement, 'busy');
            return result;
        });
        return d;
    },

    loadTree: function() {
        var self = this;
        MochiKit.DOM.addElementClass(self.contentElement, 'busy');
        var d = MochiKit.Async.doSimpleXMLHttpRequest(self.base_url);
        d.addCallback(
            function(result) {
                self.replaceTree(result.responseText);
                self.setSelected();
                MochiKit.Signal.signal(self.contentElement, 'initialload');
                MochiKit.DOM.removeElementClass(self.contentElement, 'busy');
                return result;
            });
        d.addErrback(function(error) {
            zeit.cms.log_error(error);
            return error;
        });
        return d;
    },

    replaceTree: function(content) {
        var self = this;
        MochiKit.Signal.signal(self, 'zeit.cms.BeforeTreeChangeEvent');
        self.contentElement.innerHTML = content;
        MochiKit.Signal.signal(self, 'zeit.cms.TreeChangedEvent');
        MochiKit.Signal.signal(self, 'treeChangeEvent'); // BBB
    },


    setSelected: function() {
        var self = this;
        var head = application_url + '/repository/';
        var selectable_path = context_url.slice(head.length);
        var id_base = 'http://xml.zeit.de/';
        var unique_id = id_base + selectable_path + '/';
        var element = null;
        while(isNull(element) && unique_id != id_base) {
            var elements = MochiKit.Selector.findChildElements(
                self.contentElement, ['li[uniqueId="' + unique_id + '"]']);
            if (elements.length) {
                element = elements[0];
            }
            // aka rsplit('/', 2)[0]:
            unique_id = unique_id.split('/').slice(0, -2).join('/') + '/';
        }
        while (!isNull(element) && element.hasAttribute('uniqueId'))  {
            element.setAttribute('active', 'True');
            element = MochiKit.DOM.getFirstParentByTagAndClassName(
                element, 'li', null);
        }
    }
};
