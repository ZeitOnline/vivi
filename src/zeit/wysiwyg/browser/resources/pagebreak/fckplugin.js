// Plugin for managing videos.

FCKCommands.RegisterCommand(
    'Zeit_Pagebreak' ,
    new FCKDialogCommand(
        'Seitenumbruch', 'ZEIT: Seitenumbruch',
        FCKConfig.PageConfig.ZeitResources + '/pagebreak/dialog.pt',
        380, 250));


// Create the toolbar button.
var oPagebreakItem = new FCKToolbarButton(
    'Zeit_Pagebreak', 'Seitenumbruch');
oVideoItem.IconPath = FCKConfig.PageConfig.ZeitResources+'/pagebreak/icon.jpg';
FCKToolbarItems.RegisterItem( 'Zeit_Pagebreak', oPagebreakItem);
