// Pagebreak

MochiKit.Signal.connect(window, 'onload', function(event) {
    dialog.SetOkButton(true);

    if (get_pagebreak_div() !== null) {
        var teaser = get_teaser_div().textContent;
        $('teaser').value = teaser;
    }
});


function get_pagebreak_div() {
    var selected_element = oEditor.FCKSelection.GetSelectedElement();
    if (selected_element === null) {
        selected_element = oEditor.FCKSelection.GetParentElement();
    }

    var class = 'page-break';

    if (selected_element !== null) {
        if (selected_element.nodeName != 'DIV' ||
            !MochiKit.DOM.hasElementClass(selected_element, class)) {
            try {
                selected_element = MochiKit.DOM.getFirstParentByTagAndClassName(
                    selected_element, 'div', class);
            } catch (e) {
                selected_element = null;
            }
        }
    }
    return selected_element;
}

function get_teaser_div() {
    var container = get_pagebreak_div();
    if (container === null)
        return null
    return MochiKit.DOM.getFirstElementByTagAndClassName(
        'div', 'page-break-teaser', container);
}

function Ok() {
    var teaser = GetE('teaser').value;

    oEditor.FCKUndo.SaveUndoStep();

    if (get_pagebreak_div() === null) {
        var pagebreak_div = DIV(
            {'class': 'page-break'},
            DIV({'class': 'page-break-teaser'},
                teaser));

        var selected_element = oEditor.FCKSelection.GetBoundaryParentElement();
        if (selected_element.nodeName == 'BODY') {
            selected_element.appendChild(pagebreak_div);
        } else {
            selected_element.parentNode.insertBefore(
                pagebreak_div,
                selected_element.nextSibling);
        }
        if (pagebreak_div.nextSibling === null) {
            // Note: between the ' ' there is a no break space.
            pagebreak_div.parentNode.appendChild(P({}, ' '));
        }
    } else {
        get_teaser_div().textContent = teaser;
    }

    return true;
}
