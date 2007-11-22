/* zrt-replace: "{SERVER-URL}" tal"request/getApplicationURL" */

var KeywordsWidget = ObjectSequenceWidgetBase.extend({

    initialize: function() {
        arguments.callee.$.initialize.call(this);
    },
    
    renderElement: function(index, title) {
        return LI({'class': 'element', 'index': i}, title);
    },

    showAddKeyword: function() {
        var othis = this;
        var oarguments = arguments;

        var lightbox = new gocept.Lightbox(this.element);

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
        d.addCallback(function(result) {
            othis.updateLightbox();
            return result;
        });
    },

    updateLightbox: function() {
        var othis = this;
        var ul_element = getElement('lightbox-keyword-list');
        while (ul_element.firstChild != null) {
            removeElement(ul_element.firstChild);
        }
        var amount = Number(this.getCountField().value);
        forEach(range(amount), function(i) {
            var title = othis.getTitleField(i).value;
            appendChildNodes(
                ul_element,
                LI({'class': 'element', 'index': i},
                    title, 
                     IMG({'action': 'delete',
                          'index': i,
                          'src': '/@@/zeit.cms/icons/delete.png'})));
        });
    },

    addKeyword: function(keyword_url) {
        var code_label = keyword_url.substr(10).split('/');
        var code = code_label[0];
        var label = code_label[1];
        arguments.callee.$.add.call(this, code, label);
        this.updateLightbox();
    },

    addCustomKeyword: function(keyword_code) {
        arguments.callee.$.add.call(this, keyword_code, keyword_code); 
        this.updateLightbox();
    },

    delete: function(index) {
        arguments.callee.$.delete.call(this, index);
        this.updateLightbox();
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

