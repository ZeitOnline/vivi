(function($) {

zeit.cms.declare_namespace('zeit.content.article');


var NOT_FOUND = {'node': null, 'position': -1};
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
            return {'node': node, 'position': position + start};
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
            return {'node': node, 'position': position};
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

}(jQuery));
