(function($) {

zeit.cms.declare_namespace('zeit.content.article');


var NOT_FOUND = {};


zeit.content.article.find_next = function(toplevel, text, direction) {

    var node = toplevel;
    var start = 0;
    var selection = zeit.content.article._get_selection_end(toplevel);
    if (selection) {
        node = selection['node'];
        start = selection['position'];
    }

    var match = zeit.content.article._find_below(node, text, start, direction);
    if (match != NOT_FOUND) {
        zeit.content.article.select(
            match['node'], match['position'], match['position'] + text.length);
    }
};


zeit.content.article._find_below = function(node, text, start, direction) {
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
            var match = zeit.content.article._find_below(
                child, text, /*start=*/0, direction);
            if (match != NOT_FOUND) {
                return match;
            }
        }
        return NOT_FOUND;
    }
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


zeit.content.article._get_selection_end = function(toplevel) {
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
            result = {'node': range.endContainer, 'position': range.endOffset};
        }
    }
    return result;
};

}(jQuery));
