/* zrt-replace: "{SERVER-URL}" tal"request/getApplicationURL" */

var KeywordsWidget = ObjectSequenceWidgetBase.extend({

    initialize: function() {
        arguments.callee.$.initialize.call(this);
        var new_li = LI({'class': 'new'},
                        INPUT({'type': 'button',
                               'name': 'new_keyword', 
                               'value': 'Schlüsselwort hinzufügen'})); 
        appendChildNodes(this.ul_element, new_li);
        this.drop_target = new_li;
    },

    showAddKeyword: function() {
        var othis = this;
        var oarguments = arguments;
        var lightbox_shade = DIV({'id': 'lightbox-shade'})
        var lightbox = DIV({'id': 'lightbox'});
        appendChildNodes(this.element, lightbox_shade, lightbox);
        connect(lightbox_shade, 'onclick', this, 'hideAddKeyword');
       
        var selected_keywords = []
        var amount = Number(this.getCountField().value);
        forEach(range(amount), function(i) {
            var code = oarguments.callee.$.getValueField.call(othis, i).value
            selected_keywords.push(code);
        });
       
        var url = '{SERVER-URL}/@@keyword-browser.html';
        var tree = new Tree(url, 'lightbox');
        tree.query_arguments['selected_keywords'] = serializeJSON(
            selected_keywords)
        var d = tree.loadTree();
    },

    hideAddKeyword: function() {
        removeElement('lightbox-shade');
        removeElement('lightbox');
    },

    addKeyword: function(keyword_url) {
        var code_label = keyword_url.substr(10).split('/');
        var code = code_label[0];
        var label = code_label[1];
        arguments.callee.$.add.call(this, code, label);
        this.hideAddKeyword();
    },

    addCustomKeyword: function(keyword_code) {
        arguments.callee.$.add.call(this, keyword_code, keyword_code); 
        this.hideAddKeyword();
    },

    handleClick: function(event) {
        var target = event.target();
        if (target.getAttribute('name') == 'new_keyword') {
            this.showAddKeyword();
        } else if (target.nodeName == 'A' &&
                   target.getAttribute('href').indexOf('keyword://') == 0) {
            this.addKeyword(target.getAttribute('href')); 
        } else if (target.getAttribute('name') == 'add_new_keyword_button') {
            var code = getElement('new_keyword_code').value
            this.addCustomKeyword(code);
        } else {
            arguments.callee.$.handleClick.call(this, event);
        }
    },

});

