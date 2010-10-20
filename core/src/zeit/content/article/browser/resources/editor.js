(function() {

zeit.cms.declare_namespace('zeit.content.article');


var ident = MochiKit.Signal.connect(
    zeit.edit.editor, 'script-loading-finished',
    function() {
        MochiKit.Signal.disconnect(ident);

    zeit.content.article.body_sorter = new zeit.edit.sortable.BlockSorter(
        'editable-body');
    });

// Initialize module library
MochiKit.Signal.connect(
    window, 'cp-editor-loaded', function() {
    zeit.edit.library.create(
        'article', context_url + '/editable-body', 'Artikel');
});

zeit.edit.drop.registerHandler({
    accept: ['editable-body-module'],
    activated_by: 'action-editable-body-module-droppable',
    url_attribute: 'cms:create-block-url',
    query_arguments: function(draggable) {
        return {'block_type': draggable.getAttribute('cms:block_type')};
    },
});



zeit.content.article.Editable = gocept.Class.extend({
    // Inline editing module

    construct: function(context_element) {
        var self = this;
        self.context = context_element;
        self.edited_paragraphs = [];
        self.editable = self.merge();
        self.editable.removeAttribute('cms:cp-module');
        self.editable.contentEditable = true;
        self.editable.focus();
        self.command('styleWithCSS', false);
        self.init_toolbar();
        /*MochiKit.Signal.connect(
            self.editable, 'onblur',
            self, self.save);*/
    },

    is_block_editable: function(block) {
        return !isNull(
            MochiKit.DOM.getFirstElementByTagAndClassName(
                'div', 'editable', block));
    },

    merge: function() {
        var self = this;
        var block = MochiKit.DOM.getFirstParentByTagAndClassName(
            self.context, null, 'block');
        var blocks = MochiKit.DOM.getElementsByTagAndClassName(
            null, 'block', block.parentNode);
        var i = blocks.indexOf(block);
        var paragraphs = [];
        // XXX remove code duplication
        while (i > 0) {
            i -= 1;
            if (self.is_block_editable(blocks[i])) {
                paragraphs.push(blocks[i]);
            } else {
                break;
            }
        }
        paragraphs.reverse();
        paragraphs.push(block);
        i = blocks.indexOf(block);
        while (i < blocks.length-1) {
            i += 1;
            if (self.is_block_editable(blocks[i])) {
                paragraphs.push(blocks[i]);
            } else {
                break;
            }
        }
        self.edited_paragraphs = MochiKit.Base.map(
            function(element) { return element.id; },
            paragraphs);
        var editable = MochiKit.DOM.getFirstElementByTagAndClassName(
            null, 'editable', paragraphs[0]);
        forEach(paragraphs.slice(1), function(paragraph) {
            forEach(MochiKit.Selector.findChildElements(
                paragraph, ['.editable > *']), function(p) {
                editable.appendChild(p);
            });
            MochiKit.DOM.removeElement(paragraph);
        });
        return editable;
    },

    init_toolbar: function() {
        var self = this;
        self.toolbar = self.editable.parentNode.insertBefore(
            DIV({class: 'rte-toolbar', style: 'display: block'}),
            self.editable);
        self.toolbar.innerHTML = "\
            <a rel='command' href='bold'>B</a>\
            <a rel='command' href='italic'>I</a>\
            <a rel='command' href='insertunorderedlist'>UL</a>\
            <a rel='command' href='insertorderedlist'>OL</a>\
            <a href='#' class='rteButton intertitle'>T</a>\
            <a href='#' class='rteButton paragraph'>p</a>\
            <a href='#' class='rteButton link'>a</a>\
            <a rel='method' href='save' class='rteButton'>save</a>\
            ";
        MochiKit.Signal.connect(
            self.toolbar, 'onclick',
            self, self.handle_toolbar_click);
    },

    handle_toolbar_click: function(event) {
        log('Toolbar click');
        var self = this;
        if (event.target().nodeName != 'A') {
            return;
        }
        event.stop()
        if (event.target().rel == 'command') {
            event.stop();
            var action = event.target().getAttribute('href');
            self.command(action);
        } else if (event.target().rel == 'method') {
            var method = event.target().getAttribute('href');
            self[method]();
        }
    },

    get_text_list: function() {
        var self = this;
        var result = []
        forEach(self.editable.childNodes, function(element) {
            if (element.nodeType == element.ELEMENT_NODE) {
                result.push({factory: element.nodeName.toLowerCase(),
                             text: element.innerHTML});
            }
        });
        return result;
    },

    save: function(event) {
        var self = this;
        log('Saving');
        // XXX revise disconnect
        MochiKit.Signal.disconnectAll(self.toolbar);
        // until now, the editor can only be contained in an editable-body.
        var url = $('editable-body').getAttribute('cms:url') + '/@@save_text';
        zeit.edit.makeJSONRequest(url, {
            paragraphs: self.edited_paragraphs,
            text: self.get_text_list()});

    },

    command: function(command, option) {
        var self = this;
        try {
            document.execCommand(command, false, option);
        } catch(e) {
			window.console && console.log(e)
		}
		//this._updateToolbar();
    }

});

})();
