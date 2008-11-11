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
        GetE('videoId').value = /.*=(.*)$/.exec(selected_element.value)[1];
    }
}, false);


function Ok() {
    var video_id = GetE('videoId').value;
    if (!video_id) {
        GetE('videoId').focus();
        alert('Die Video-Id muss ausgefüllt werden.');
        return false;
    }
    oEditor.FCKUndo.SaveUndoStep();

    var input = oEditor.FCKSelection.GetSelectedElement();
    if (input == null) {
        var input = FCK.EditorDocument.createElement('INPUT');
        var selected_element = oEditor.FCKSelection.GetParentElement();
        selected_element.parentNode.insertBefore(
            new_node, 
            selected_element.nextSibling);
    }
     
    input.value = 'video_article: videoID=' + video_id;
    input.type = 'text';
    input.size = 60;

    return true;
}
