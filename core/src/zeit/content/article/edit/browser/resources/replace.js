(function($) {

zeit.cms.declare_namespace('zeit.content.article');


var NOT_FOUND = {'node': null, 'position': -1, text: null};
zeit.content.article.NOT_FOUND = NOT_FOUND;


var FORWARD = 'forward';
var BACKWARD = 'backward';
zeit.content.article.FORWARD = FORWARD;
zeit.content.article.BACKWARD = BACKWARD;


zeit.content.article.find_next = function(toplevel, text, direction) {
    if (! direction) {
        direction = FORWARD;
    }
    var find_below = zeit.content.article['_find_below_' + direction];

    var node = toplevel;
    var start = 0;
    var selection = zeit.content.article._get_selection(toplevel, direction);
    if (selection) {
        node = selection['node'];
        start = selection['position'];
    }

    var match;
    while (true) {
        match = find_below(node, text, start);
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


zeit.content.article._find_below_forward = function(node, text, start) {
    if (node.nodeType == node.TEXT_NODE) {
        var haystack = node.textContent.substring(start);
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
                child, text, /*start=*/0);
            if (match != NOT_FOUND) {
                return match;
            }
        }
        return NOT_FOUND;
    }
};


zeit.content.article._find_below_backward = function(node, text, start) {
    if (node.nodeType == node.TEXT_NODE) {
        var haystack = node.textContent.substring(0, start);
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
                child, text, /*start=*/undefined);
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


zeit.content.article._get_selection = function(toplevel, direction) {
    var result = null;
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
        if (inside_toplevel) {
            if (direction == FORWARD) {
                result = {'node': range.endContainer,
                          'position': range.endOffset};
            } else {
                result = {'node': range.startContainer,
                          'position': range.startOffset};
            }
        }
    }
    return result;
};


zeit.content.article.FindDialog = gocept.Class.extend({

    TEMPLATE: '\
<div id="find-dialog"> \
  <p><label for="find-dialog-searchtext">Suchen nach</label> \
  <input type="text" id="find-dialog-searchtext" /></p> \
  <p><label for="find-dialog-replacement">Ersetzen mit</label> \
  <input type="text" id="find-dialog-replacement" /></p> \
</div>',

    construct: function(editable) {
        var self = this;
        self.editable = editable;
        self.restore_selection = {};
        if (window.getSelection().rangeCount) {
            var range = window.getSelection().getRangeAt(0);
            self.restore_selection['node'] = range.startContainer;
            self.restore_selection['start'] = range.startOffset;
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
                'buttons': [
                    {'text': 'Ersetzen',
                     click: MochiKit.Base.bind(self.replace_current, self)},
                    {'text': 'Zurück',
                     click: MochiKit.Base.bind(self.goto_prev, self)},
                    {'text': 'Weiter',
                     click: MochiKit.Base.bind(self.goto_next, self)}
                ]
            });
            self.form.on('keydown', function(event) {
                if (event.which == 13) {
                    event.preventDefault();
                    this._find_dialog.goto_next();
                }
            });
            self.form.on('dialogclose', function() {
                this._find_dialog.close();
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
        if (self.restore_selection) {
            window.getSelection().removeAllRanges();
            zeit.content.article.select(
                self.restore_selection['node'],
                self.restore_selection['start'],
                self.restore_selection['start']);
            //self.restore_selection['node'].parentNode.scrollIntoView();
        }
    },

    goto_prev: function() {
        var self = this;
        self.find(zeit.content.article.FORWARD);
    },

    goto_next: function() {
        var self = this;
        self.find(zeit.content.article.BACKWARD);
    },

    find: function(direction) {
        var self = this;
        self.current_match = self.editable.find_and_select_next(
            $('#find-dialog-searchtext').val(), direction);
        if (self.current_match == NOT_FOUND) {
            alert('Keine weiteren Ergebnisse');
        } else {
            self.current_match['node'].parentNode.scrollIntoView();
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
    }

});

}(jQuery));
