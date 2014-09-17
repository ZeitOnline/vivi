(function($) {

zeit.cms.declare_namespace('zeit.content.article');


var NOT_FOUND = {'node': null, 'position': -1, text: null};
zeit.content.article.NOT_FOUND = NOT_FOUND;


var FORWARD = 'forward';
var BACKWARD = 'backward';
zeit.content.article.FORWARD = FORWARD;
zeit.content.article.BACKWARD = BACKWARD;


zeit.content.article.find_next = function(
    toplevel, text, direction, case_sensitive, selection) {
    if (! direction) {
        direction = FORWARD;
    }
    var find_below = zeit.content.article['_find_below_' + direction];

    var node = toplevel;
    var start = 0;
    if (isUndefined(selection)) {
        selection = zeit.content.article._get_selection(toplevel);
    }
    if (selection && selection['inside_toplevel']) {
        if (direction == FORWARD) {
            node = selection['endContainer'];
            start = selection['endOffset'];
        } else {
            node = selection['startContainer'];
            start = selection['startOffset'];
        }
    }

    var match;
    while (true) {
        match = find_below(node, text, start, case_sensitive);
        if (match != NOT_FOUND) {
            zeit.content.article.select(
                match['node'],
                match['position'],
                match['position'] + text.length);
            return match;
        }
        node = zeit.content.article._next_candidate(toplevel, node, direction);
        if (node == null) {
            break;
        }
        // The selection only matters for the very first node, so we reset it.
        if (direction == FORWARD) {
            start = 0;
        } else {
            start = undefined;
        }
    }
    return NOT_FOUND;
};


zeit.content.article._find_below_forward = function(
    node, text, start, case_sensitive) {
    if (node.nodeType == node.TEXT_NODE) {
        var haystack = node.textContent.substring(start);
        if (!case_sensitive) {
            haystack = haystack.toLowerCase();
            text = text.toLowerCase();
        }
        var position = haystack.indexOf(text);
        if (position != -1) {
            return {'node': node, 'position': position + start, 'text': text};
        } else {
            return NOT_FOUND;
        }
    } else {
        for (var i = 0; i < node.childNodes.length; i++) {
            var child = node.childNodes[i];
            var match = zeit.content.article._find_below_forward(
                child, text, /*start=*/0, case_sensitive);
            if (match != NOT_FOUND) {
                return match;
            }
        }
        return NOT_FOUND;
    }
};


zeit.content.article._find_below_backward = function(
    node, text, start, case_sensitive) {
    if (node.nodeType == node.TEXT_NODE) {
        var haystack = node.textContent.substring(0, start);
        if (!case_sensitive) {
            haystack = haystack.toLowerCase();
            text = text.toLowerCase();
        }
        var position = haystack.lastIndexOf(text);
        if (position != -1) {
            return {'node': node, 'position': position, 'text': text};
        } else {
            return NOT_FOUND;
        }
    } else {
        for (var i = node.childNodes.length - 1; i >= 0; i--) {
            var child = node.childNodes[i];
            var match = zeit.content.article._find_below_backward(
                child, text, /*start=*/undefined, case_sensitive);
            if (match != NOT_FOUND) {
                return match;
            }
        }
        return NOT_FOUND;
    }
};


zeit.content.article._next_candidate = function(toplevel, node, direction) {
    if (node == toplevel) {
        return null;
    }
    var relation = (direction == FORWARD) ? 'nextSibling' : 'previousSibling';
    if (node[relation]) {
        return node[relation];
    }
    return zeit.content.article._next_candidate(
        toplevel, node.parentNode, direction);
};


zeit.content.article.select = function(node, start, end) {
    var range;
    if (window.getSelection().rangeCount == 0) {
        range = document.createRange();
        window.getSelection().addRange(range);
    } else {
        range = window.getSelection().getRangeAt(0);
    }
    range.setStart(node, start);
    range.setEnd(node, end);
};


zeit.content.article._get_selection = function(toplevel) {
    if (window.getSelection().rangeCount) {
        var range = window.getSelection().getRangeAt(0);
        var selected_node = range.endContainer;
        var inside_toplevel = false;
        while (selected_node != null) {
            selected_node = selected_node.parentNode;
            if (selected_node == toplevel) {
                inside_toplevel = true;
                break;
            }
        }
        return {
            'inside_toplevel': inside_toplevel,
            'startContainer': range.startContainer,
            'startOffset': range.startOffset,
            'endContainer': range.endContainer,
            'endOffset': range.endOffset
        };
    }
    return null;
};


zeit.content.article.FindDialog = gocept.Class.extend({

    TEMPLATE: '\
<div id="find-dialog"> \
  <p><label for="find-dialog-searchtext">Suchen nach</label> \
  <input type="text" id="find-dialog-searchtext" /></p> \
  <p><label for="find-dialog-replacement">Ersetzen durch</label> \
  <input type="text" id="find-dialog-replacement" /></p> \
  <p><label><input type="checkbox" id="find-dialog-case"/> \
    Groß/Kleinschreibung beachten</label></p> \
</div>',

    construct: function(editable) {
        var self = this;
        self.editable = editable;
        self.restore_selection = null;
        self.start_selection = null;
        var selection = zeit.content.article._get_selection(
            self.editable.editable);
        if (selection) {
            self.restore_selection = selection;
            if (selection['inside_toplevel']) {
                self.start_selection = selection;
            }
        }
        self.init_form();
        self.current_match = NOT_FOUND;
    },

    init_form: function() {
        var self = this;
        self.form = $('#find-dialog');
        if (! self.form.length) {
            self.form = $(self.TEMPLATE).appendTo($('body'));
            self.form.dialog({
                'modal': true,
                'title': 'Suchen und Ersetzen',
                'dialogClass': 'find-dialog',
                'width': 500,
                'buttons': [
                    {'text': 'Ersetzen',
                     click: function() {
                         this._find_dialog.replace_current(); }},
                    {'text': 'Alles ersetzen',
                     click: function() {
                         this._find_dialog.replace_all(); }},
                    {'text': '< Zurück',
                     click: function() { this._find_dialog.goto_prev(); }},
                    {'text': 'Weiter >',
                     click: function() { this._find_dialog.goto_next(); }}
                ]
            });
            self.form.on('keydown', function(event) {
                if (event.which == 13) {
                    event.preventDefault();
                    this._find_dialog.goto_next();
                }
            });
            self.form.on('dialogclose', function() {
                this._find_dialog.on_close();
            });
        }
        self.form.dialog(
            'option', 'position',
            { my: "center", at: "center", of: window });
        $('#find-dialog-searchtext').val('');
        $('#find-dialog-replacement').val('');
        self.form[0]._find_dialog = self;
    },

    show: function() {
        var self = this;
        self.form.dialog('open');
    },

    close: function() {
        var self = this;
        self.form.dialog('close');
    },

    on_close: function() {
        var self = this;
        if (self.restore_selection) {
            window.getSelection().removeAllRanges();
            zeit.content.article.select(
                self.restore_selection['startContainer'],
                self.restore_selection['startOffset'],
                self.restore_selection['startOffset']);
            // I think we don't want to scollIntoView, since I think the most
            // common scenario for restore_selection is closing the dialog
            // after not finding anything, which means there will have been
            // no scrolling away anyway.
            // self.restore_selection[
            //     'startContainer'].parentNode.scrollIntoView();
        }
        self.editable.editable.focus();
    },

    goto_prev: function() {
        var self = this;
        self.find(zeit.content.article.BACKWARD);
    },

    goto_next: function() {
        var self = this;
        self.find(zeit.content.article.FORWARD);
    },

    find: function(direction) {
        var self = this;
        self.current_match = self.editable.find_and_select_next(
            $('#find-dialog-searchtext').val(), direction,
            $('#find-dialog-case').attr('checked'), self.start_selection);
        self.start_selection = undefined;
        if (self.current_match == NOT_FOUND) {
            var relation = (
                direction == FORWARD) ? 'nextSibling' : 'previousSibling';
            var next_editable = self.editable.activate_next_editable(
                relation, /*suppress_focus=*/true);
            if (next_editable !== null) {
                self.editable = next_editable;
                self.restore_selection = null;
                self.editable.initialized.addCallback(function(){
                    self.find(direction);
                });
            } else {
                alert('Keine weiteren Ergebnisse');
            }
        } else {
            self.current_match['node'].parentNode.scrollIntoView();
            self.restore_selection = null;
        }
    },

    replace_current: function() {
        var self = this;
        if (self.current_match == NOT_FOUND) {
            return;
        }
        var match = self.current_match;
        self.editable.replace_text(
            match['node'], match['position'],
            match['position'] + match['text'].length,
            $('#find-dialog-replacement').val());
    },

    replace_all: function() {
        var self = this;
        var find = $('#find-dialog-searchtext').val();
        var replace = $('#find-dialog-replacement').val();
        if (! find) {
            alert('Bitte Suchtext eingeben.');
            return;
        }
        var d = self.editable.replace_all(find, replace);
        d.addCallback(function() { self.close(); });
    }

});


zeit.content.article.display_replace_count = function(count) {
    alert(count + ' Stelle(n) ersetzt.');
};


MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {
    if (! zeit.cms.in_article_editor()) {
        return;
    }

    MochiKit.Signal.connect(
        zeit.edit.editor, 'after-replace-all',
        zeit.content.article.display_replace_count);
});

}(jQuery));
