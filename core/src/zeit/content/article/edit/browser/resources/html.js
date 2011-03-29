(function() {

zeit.cms.declare_namespace('zeit.content.article.html');


zeit.content.article.html.to_xml = function(tree) {
    var steps = [
        translate_tags,
        kill_empty_p,
    ];

    forEach(steps, function(step) { step(tree); });
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
        var tag = el.nodeName.toLowerCase();
        if (tag in mapping) {
            zeit.content.article.html.change_tag(el, mapping[tag]);
        }
        translate_tags(el);
    });
};


function kill_empty_p(tree) {
    forEach(tree.childNodes, function(el) {
        var tag = el.nodeName.toLowerCase();
        if (tag == 'p' && ! el.hasChildNodes()) {
            MochiKit.DOM.removeElement(el);
        }
    });
};

})();