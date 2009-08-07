// Plugin for mailform

var ZeitRelatedCommand = function() {
    this.Name = 'Zeit_Related';
}

ZeitRelatedCommand.prototype = {

    Execute: function() {
        var div = FCK.EditorDocument.createElement('DIV');
        div.innerHTML = '&nbsp;';
        div.setAttribute('class', 'related inline-element');
        FCK.InsertElement(div);
    },

    GetState: function() {
        if ( FCK.EditMode != FCK_EDITMODE_WYSIWYG )
            return FCK_TRISTATE_DISABLED ;
        return FCK_TRISTATE_OFF;
    },
};


FCKCommands.RegisterCommand(
    'Zeit_Related' ,
    new ZeitRelatedCommand());


// Create the toolbar button.
var oItem = new FCKToolbarButton(
    'Zeit_Related', 'Related');
oItem.IconPath =
    FCKConfig.PageConfig.ZeitResources+ '/related/icon.png';
FCKToolbarItems.RegisterItem('Zeit_Related', oItem);
        
