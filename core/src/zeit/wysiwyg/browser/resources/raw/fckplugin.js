// Plugin for "raw"

FCKCommands.RegisterCommand(
    'Zeit_RAW' ,
    new FCKDialogCommand(
        'RAW', 'ZEIT: RAW',
        FCKConfig.PageConfig.ZeitResources + '/raw/dialog.pt',
        800, 600));


// Create the toolbar button.
var oRawItem = new FCKToolbarButton(
    'Zeit_RAW', 'Raw');
oRawItem.IconPath = FCKConfig.PageConfig.ZeitResources + '/raw/raw.png'

FCKToolbarItems.RegisterItem('Zeit_RAW', oRawItem);
