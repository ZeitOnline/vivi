// Plugin for mailform

var ZeitMailFormCommand = function() {
    this.Name = 'Zeit_MailForm';
}

ZeitMailFormCommand.prototype = {

    Execute: function() {
        var input = FCK.EditorDocument.createElement('INPUT');
        var selected_element = 
            FCKSelection.GetBoundaryParentElement();
        selected_element.parentNode.insertBefore(
            input, 
            selected_element.nextSibling);
        input.setAttribute('value', 'mailformular');
        input.setAttribute('type', 'text');
        input.setAttribute('size', '60');
    },

    GetState: function() {
        if ( FCK.EditMode != FCK_EDITMODE_WYSIWYG )
            return FCK_TRISTATE_DISABLED ;
        return FCK_TRISTATE_OFF;
    },
};


FCKCommands.RegisterCommand(
    'Zeit_MailForm' ,
    new ZeitMailFormCommand());


// Create the toolbar button.
var oMailItem = new FCKToolbarButton(
    'Zeit_MailForm', 'MailForm');
oMailItem.IconPath =
    FCKConfig.PageConfig.ZeitResources+ '/mailform/mail_icon.png';
FCKToolbarItems.RegisterItem('Zeit_MailForm', oMailItem);
        
