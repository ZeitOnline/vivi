(function() {

zeit.cms.declare_namespace('zeit.content.article.html');


zeit.content.article.html.to_xml = function(tree) {
    var steps = [
        translate_tags,
        kill_empty_p,
        replace_double_br_with_p,
        escape_missing_href,
    ];

    forEach(steps, function(step) {
        step(tree);
    });
    return tree;
};


zeit.content.article.html.change_tag = function(element, new_name) {
    var new_element = MochiKit.DOM.swapDOM(
        element,
        MochiKit.DOM.createDOM(new_name));
    while (element.firstChild) {
        new_element.appendChild(element.firstChild);
    }
};


function translate_tags(tree) {
    var mapping = {
        'b': 'strong',
        'i': 'em',
        'div': 'p',
        'h3': 'intertitle',
    };

    forEach(tree.childNodes, function(el) {
        if (tag(el) in mapping) {
            zeit.content.article.html.change_tag(el, mapping[tag(el)]);
        }
        translate_tags(el);
    });
};


function kill_empty_p(tree) {
    forEach(tree.childNodes, function(el) {
        if (tag(el) == 'p' && ! el.hasChildNodes()) {
            MochiKit.DOM.removeElement(el);
        } else {
            kill_empty_p(el);
        }
    });
};


function replace_double_br_with_p(tree) {
    forEach(tree.childNodes, function(el) {
        var sibling = nextSiblingElement(el);
        if (! (tag(el) == 'br' && tag(sibling) == 'br')) {
            replace_double_br_with_p(el);
            return;
        }

        var p = MochiKit.DOM.createDOM('p')
        if (tag(sibling.nextSibling) == el.TEXT_NODE) {
            p.appendChild(sibling.nextSibling);
        }
        MochiKit.DOM.removeElement(el);
        MochiKit.DOM.swapDOM(sibling, p);
    });
};


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
};


// helper functions

function tag(element) {
    if (MochiKit.Base.isNull(element)) {
        return null;
    }
    if (element.nodeType != element.ELEMENT_NODE) {
        return element.nodeType;
    }
    return element.nodeName.toLowerCase();
};


function nextSiblingElement(element) {
    var el = element.nextSibling;
    while (el) {
        if (el.nodeType == el.ELEMENT_NODE) {
            return el;
        }
        el = el.nextSibling;
    }
    return null;
};

})();