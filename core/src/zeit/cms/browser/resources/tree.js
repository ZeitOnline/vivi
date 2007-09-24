function Tree(base_url, element_id) {
    this.base_url = base_url + '/';
    this.contentElement = getElement(element_id);
    connect(this.contentElement, 'onclick', this, 'clickHandler');
    this.query_arguments = {}
}

Tree.prototype = {
    clickHandler: function(event) {
        var target = event.target();
        var action = target.getAttribute('action');
        if (action == null)
            return;
        
        this.changeState(target, action)
    },

    changeState: function(node, action) {
        var tree = this;
        var uniqueId = node.getAttribute('uniqueId');
        var url = this.base_url + '@@' + action + 'Tree' ;
        var query = {'uniqueId': uniqueId};
        update(query, this.query_arguments);
        var d = doSimpleXMLHttpRequest(url, query);
        d.addCallbacks(
            function(result) {
                tree.replaceTree(result.responseText);
                return result;
            })
    },

    loadTree: function() {
        var tree = this;
        var d = doSimpleXMLHttpRequest(this.base_url);
        d.addCallbacks(
            function(result) {
                tree.replaceTree(result.responseText);
                signal(tree.contentElement, 'initialload');
                return result;
            })
        return d;
    },

    replaceTree: function(content) {
        this.contentElement.innerHTML = content;
        signal(this, 'treeChangeEvent');
    },
}
