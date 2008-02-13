var KeywordsWidget = ObjectSequenceWidgetBase.extend({

    renderElement: function(index, title) {
        return LI({'class': 'element', 'index': i}, title);
    },

    showAddKeyword: function() {
        var othis = this;
        var oarguments = arguments;

        var lightbox = new gocept.Lightbox(
            getFirstElementByTagAndClassName('body'));
        connect(lightbox.content_box, 'onclick', this, 'handleClick');

        var selected_keywords = []
        var amount = Number(this.getCountField().value);
        forEach(range(amount), function(i) {
            var code = oarguments.callee.$.getValueField.call(othis, i).value
            selected_keywords.push(code);
        });

        var url = '/@@keyword-browser.html';
        var tree = new Tree(url, 'lightbox');
        tree.query_arguments['selected_keywords'] = serializeJSON(
            selected_keywords)
        connect(tree, 'state-changed', othis, 'updateLightbox');
        var d = tree.loadTree();
        d.addCallback(function(result) {
            othis.updateLightbox();
            return result;
        });
        // typeahead
        d.addCallback(function(result) {
            othis.connectTypeAhead();
        })


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
        othis.connectTypeAhead()
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

    updateTypeaheadResults: function(responseText) {
        var text = responseText;
        this.typeahead_container.innerHTML = text;
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
        } else if (target.getAttribute('class') == 'FoundKeywordInTaxonomy') {
            this.addKeyword(target.getAttribute('href'));
        } else {
            arguments.callee.$.handleClick.call(this, event);
        }
    },

    handleTextinput: function(event) {
        var target = event.target();
        if (target.getAttribute('name') == 'new_keyword_code') {
            this.typeaheadSearch(target.value);
        }
    },

    typeaheadSearch: function(searchterm) {
        var searchTerm = searchterm; 

        var url = '/@@keyword-typeahead'
        var query = {'searchTerm': searchTerm};
        var d = doSimpleXMLHttpRequest(url, query);
        d.addCallbacks(
          function(result) {
              widget.updateTypeaheadResults(result.responseText);
          })

    },

    connectTypeAhead: function() {
        this.typeahead_container = $('keyword-typeahead-results');
        var textinput = $('new_keyword_code');
        connect(textinput, 'onkeyup', this, 'handleTextinput');
    },

});

