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

    add: function(code, label) {
        var found = false;
        this.iterFields(function(value_field, title_field) {
            if (value_field.value == code) {
                found = true;
                throw StopIteration; 
            }
        });
        if (!found) {
            arguments.callee.$.add.call(this, code, label);
        }
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
        this.add(code, label);
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
        var handled_here = true;
        if (target.getAttribute('name') == 'new_keyword') {
            this.showAddKeyword();
        } else if (target.nodeName == 'A' &&
                   target.getAttribute('href').indexOf('keyword://') == 0) {
            this.addKeyword(target.getAttribute('href'));
        } else if (target.getAttribute('class') == 'FoundKeywordInTaxonomy') {
            this.addKeyword(target.getAttribute('href'));
        } else {
            arguments.callee.$.handleClick.call(this, event);
            handled_here = false;
        }
        if (handled_here) {
            event.stop();
        }
    },

    handleTextinput: function(event) {
        var target = event.target();
        if (target.getAttribute('name') == 'new_keyword_code') {
            this.typeaheadSearch(target.value);
        }
    },

    typeaheadSearch: function(searchterm) {
        if (this.typeahead_deferred != null) {
            this.typeahead_deferred.cancel()
        }

        var searchTerm = searchterm; 
        var url = '/@@keyword-typeahead'
        var query = {'searchTerm': searchTerm};
        var d = callLater(0.2, doSimpleXMLHttpRequest, url, query);
        d.addCallbacks(
          function(result) {
              widget.updateTypeaheadResults(result.responseText);
        });
        this.typeahead_deferred = d;

    },

    connectTypeAhead: function() {
        this.typeahead_container = $('keyword-typeahead-results');
        this.typeahead_deferred = null;
        var textinput = $('new_keyword_code');
        connect(textinput, 'onkeyup', this, 'handleTextinput');
    },

    getTitleFieldName: function(index) {
        return this.widget_id + '.title.' + index;
    },

    getTitleField: function(index) {
        return getElement(this.getTitleFieldName(index));
    }


});
