// common functions for all Zeit FCKEditor dialog commands

var dialog = window.parent;
var oEditor = dialog.InnerDialogLoaded();
var FCK = oEditor.FCK;
var FCKLang = oEditor.FCKLang;
var FCKConfig = oEditor.FCKConfig;
var FCKTools = oEditor.FCKTools;

function Import(src) {
   document.write('<scr'+'ipt type="text/javascript" src="' + src + '"></sc' + 'ript>');
}


Import(FCKConfig.FullBasePath + 'dialog/common/fck_dialog_common.js');


function setSkinCSS() {
    if (FCKTools.GetStyleHtml) {
        document.write(FCKTools.GetStyleHtml(GetCommonDialogCss(FCKConfig.FullBasePath + 'dialog/')));
    } else {
        document.write( '<link href="' + oEditor.FCKConfig.SkinPath + 'fck_dialog.css" type="text/css" rel="stylesheet"/>' ) ;
    }
}