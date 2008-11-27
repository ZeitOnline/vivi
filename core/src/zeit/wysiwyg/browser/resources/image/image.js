// Image

function Import(aSrc) {
   document.write('<scr'+'ipt type="text/javascript" src="' + aSrc + '"></sc' + 'ript>');
}


var dialog = window.parent;
var oEditor = dialog.InnerDialogLoaded();
var oPage = oEditor.parent;
var FCKConfig = oEditor.FCKConfig;
var FCK = oEditor.FCK;

Import(FCKConfig.FullBasePath + 'dialog/common/fck_dialog_common.js');

MochiKit.Signal.connect(window, 'onload', function(event) {
    dialog.SetOkButton(true);

    var browse_url = oPage.context_url + '/@@default-browsing-location';
    new ObjectReferenceWidget('select-image', browse_url, 'images', false);

    MochiKit.Signal.connect('image', 'onchange', function(event) {
        var image = $('image');
        var preview = $('preview');
        var unique_id = image.value;
        preview.innerHTML = ''
        if (unique_id) {
            preview.appendChild(IMG({'src': id_to_url(unique_id)}));
        }
    });

    if (get_image() !== null) {
        var image = get_image().src;
        $('image').value = url_to_id(image);
        MochiKit.Signal.signal('image', 'onchange');
    }
});


function get_image() {
    var img = oEditor.FCKSelection.GetSelectedElement();
    if (img === null || img.nodeName != 'IMG') {
        return null;
    }
    return img;
}


function id_to_url(unique_id) {
    return unique_id.replace(
        'http://xml.zeit.de', oPage.application_url + '/repository');
}

function url_to_id(url) {
    return url.replace(
        oPage.application_url + '/repository', 'http://xml.zeit.de');
}


function Ok() {
    var unique_id = $('image').value;
    if (!unique_id) {
        alert('Die Bild-URL wird benötigt.');
        return false;
    }

    oEditor.FCKUndo.SaveUndoStep();

    var image_display_url = id_to_url(unique_id);
    var image = get_image();
    if (image === null) {
        var image = IMG({'src': image_display_url});
        FCK.InsertElement(image);
    } else {
        image.src = image_display_url;
    }

    return true;
}
