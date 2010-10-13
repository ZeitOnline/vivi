(function() {

zeit.cms.declare_namespace('zeit.content.article');


var ident = MochiKit.Signal.connect(
    zeit.edit.editor, 'script-loading-finished',
    function() {
        MochiKit.Signal.disconnect(ident);

    zeit.content.article.body_sorter = new zeit.edit.sortable.BlockSorter(
        'editable-body');
    });


zeit.content.article.Editable = gocept.Class.extend({
    // Inline editing module

    construct: function(context_element) {
        var self = this;
        self.context = context_element;
        self.edited_paragraphs = [];
        self.editable = self.merge();
        self.editable.contentEditable = true;
        self.editable.focus();
        self.command('styleWithCSS', false);
        MochiKit.Signal.connect(self.editable, 'onblur', self, self.save);
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
            if (MochiKit.DOM.hasElementClass(blocks[i], 'type-paragraph')) {
                paragraphs.push(blocks[i]);
            } else {
                break;
            }
        }
        paragraphs.reverse();
        paragraphs.push(block);
        i = blocks.indexOf(block);
        while (i < blocks.length) {
            i += 1;
            if (MochiKit.DOM.hasElementClass(blocks[i], 'type-paragraph')) {
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
                paragraph, ['.editable p']), function(p) {
                editable.appendChild(p);
            });
            MochiKit.DOM.removeElement(paragraph);
        });
        return editable;
    },

    get_text_list: function() {
        var self = this;
        return MochiKit.Base.map(
            function(p) { return p.innerHTML; },
            MochiKit.DOM.getElementsByTagAndClassName(
                'p', null, self.editable));
    },

    save: function() {
        var self = this;
        MochiKit.Signal.disconnectAll(self.editable, 'onblur');
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
