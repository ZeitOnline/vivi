// RAW

function Import(aSrc) {
   document.write('<scr'+'ipt type="text/javascript" src="' + aSrc + '"></sc' + 'ript>');
}


var dialog = window.parent;
var oEditor = dialog.InnerDialogLoaded();
var oPage = oEditor.parent;
var FCKConfig = oEditor.FCKConfig;
var FCKTools = oEditor.FCKTools;

Import(FCKConfig.FullBasePath + 'dialog/common/fck_dialog_common.js');

MochiKit.Signal.connect(window, 'onload', function(event) {
    dialog.SetOkButton(true);

    if (get_raw_area() !== null) {
        var raw = get_raw_area().textContent;
        $('raw').value = raw;
    }
});


function get_raw_area() {
    var selected_element = oEditor.FCKSelection.GetSelectedElement();
    if (selected_element === null) {
        selected_element = oEditor.FCKSelection.GetParentElement();
    }

    if (selected_element !== null) {
        if (selected_element.nodeName != 'DIV' ||
            !MochiKit.DOM.hasElementClass(selected_element, 'raw')) {
            try {
                selected_element = MochiKit.DOM.getFirstParentByTagAndClassName(
                    selected_element, 'div', 'raw');
            } catch (e) {
                selected_element = null;
            }
        }
    }
    return selected_element;
}

function Ok() {
    var content = $('raw').value;

    oEditor.FCKUndo.SaveUndoStep();

    var raw_area = get_raw_area();
    if (raw_area === null) {
        var raw_area = DIV({'class': 'raw'}, content);
        var selected_element = oEditor.FCKSelection.GetBoundaryParentElement();
        selected_element.parentNode.insertBefore(
            raw_area, 
            selected_element.nextSibling);
    } else {
        raw_area.textContent = content;
    }

    return true;
}
