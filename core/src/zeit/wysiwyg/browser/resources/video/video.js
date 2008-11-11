// Video

function Import(aSrc) {
   document.write('<scr'+'ipt type="text/javascript" src="' + aSrc + '"></sc' + 'ript>');
}


var dialog		= window.parent ;
var oEditor		= dialog.InnerDialogLoaded() ;
var FCK			= oEditor.FCK ;
var FCKLang		= oEditor.FCKLang ;
var FCKConfig	= oEditor.FCKConfig ;
var FCKTools	= oEditor.FCKTools ;

Import(FCKConfig.FullBasePath + 'dialog/common/fck_dialog_common.js');

window.addEventListener('load', function() {
	dialog.SetOkButton(true);
    
    var selected_element = oEditor.FCKSelection.GetSelectedElement();
    if (selected_element) {
        var m;
        m = /.* videoID=([^ ]+)/.exec(selected_element.value);
        if (m != null)
            GetE('videoId').value = m[1];

        m = /.* expires=([^ ]+)/.exec(selected_element.value);
        if (m != null)
            GetE('expires').value = m[1];
    }
}, false);


function Ok() {
    var video_id = GetE('videoId').value;
    var expires = GetE('expires').value;
    if (!video_id) {
        GetE('videoId').focus();
        alert('Die Video-Id muss ausgefüllt werden.');
        return false;
    }
    oEditor.FCKUndo.SaveUndoStep();

    var input = oEditor.FCKSelection.GetSelectedElement();
    if (input == null) {
        var input = FCK.EditorDocument.createElement('INPUT');
        var selected_element = oEditor.FCKSelection.GetBoundaryParentElement();
        selected_element.parentNode.insertBefore(
            input, 
            selected_element.nextSibling);
    }
     
    var value = 'video_article: videoID=' + video_id + ' expires=' + expires;
    input.setAttribute('value', value);
    input.value = value;
    input.setAttribute('type', 'text');
    input.setAttribute('size', '60');

    return true;
}
