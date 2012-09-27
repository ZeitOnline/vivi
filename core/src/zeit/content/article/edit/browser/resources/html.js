(function() {

zeit.cms.declare_namespace('zeit.content.article.html');


zeit.content.article.html.to_xml = function(tree) {
    var steps = [
        wrap_toplevel_children_in_p,
        translate_tags,
        kill_empty_p,
        replace_double_br_with_p,
        escape_missing_href
    ];

    // XXX dropping unknown tags but keeping their text is still implemented on
    // the server side (see zeit.content.article.paragraph), because there we
    // can utilize lxml.html.clean there which additionally cleans up any cruft
    // (handy for, say, pastes from MS Word). But from an architecture point of
    // view this too should be done as a step here.

    forEach(steps, function(step) {
        step(tree);
    });
    return tree;
};


zeit.content.article.html.change_tag = function(element, new_name) {
    var new_element = MochiKit.DOM.swapDOM(
        element, MochiKit.DOM.createDOM(new_name));
    while (element.firstChild) {
        new_element.appendChild(element.firstChild);
    }
};


// conversion steps

function translate_tags(tree) {
    var mapping = {
        'b': 'strong',
        'i': 'em',
        'div': 'p',
        'h3': 'intertitle'
    };

    forEach(tree.childNodes, function(el) {
        if (tag(el) in mapping) {
            zeit.content.article.html.change_tag(el, mapping[tag(el)]);
        }
        translate_tags(el);
    });
}


function kill_empty_p(tree) {
    forEach(tree.childNodes, function(el) {
        if (tag(el) == 'p' && ! el.hasChildNodes()) {
            MochiKit.DOM.removeElement(el);
        } else {
            kill_empty_p(el);
        }
    });
}


function replace_double_br_with_p(tree) {
    forEach(tree.childNodes, function(el) {
        var sibling = nextSiblingElement(el);
        if (! (tag(el) == 'br' && tag(sibling) == 'br')) {
            replace_double_br_with_p(el);
            return;
        }

        var p = MochiKit.DOM.createDOM('p');
        if (tag(sibling.nextSibling) == el.TEXT_NODE) {
            p.appendChild(sibling.nextSibling);
        }
        MochiKit.DOM.removeElement(el);
        MochiKit.DOM.swapDOM(sibling, p);
    });
}


function escape_missing_href(tree) {
    forEach(tree.childNodes, function(el) {
        if (tag(el) != 'a') {
            escape_missing_href(el);
            return;
        }

        if (! el.hasAttribute('href')) {
            el.setAttribute('href', '#');
        }
    });
}


function wrap_toplevel_children_in_p(tree) {
    var collect = [];

    var wrap_in_p = function(items) {
        var p = MochiKit.DOM.createDOM('p');
        while (items.length) {
            p.appendChild(items.shift());
        }
        return p;
    };

    forEach(tree.childNodes, function(el) {
        if (el.nodeType == el.TEXT_NODE || display(el) == 'inline') {
            collect.push(el);
        } else {
            if (collect.length) {
                MochiKit.DOM.insertSiblingNodesBefore(el, wrap_in_p(collect));
            }
        }
    });

    if (collect.length) {
        tree.appendChild(wrap_in_p(collect));
    }
}


// helper functions

function tag(element) {
    if (MochiKit.Base.isNull(element)) {
        return null;
    }
    if (element.nodeType != element.ELEMENT_NODE) {
        return element.nodeType;
    }
    return element.nodeName.toLowerCase();
}


function nextSiblingElement(element) {
    var el = element.nextSibling;
    while (el) {
        if (el.nodeType == el.ELEMENT_NODE) {
            return el;
        }
        el = el.nextSibling;
    }
    return null;
}


function display(element) {
    if (element.nodeType != element.ELEMENT_NODE) {
        return null;
    }
    return MochiKit.Style.getStyle(element, 'display');
}

}());
