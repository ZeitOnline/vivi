FCKCommands.RegisterCommand(
    'Zeit_RAW' ,
    new FCKDialogCommand(
        'RAW', 'ZEIT: RAW',
        FCKConfig.PageConfig.ZeitResources + '/raw/dialog.pt',
        800, 600));
var button = new FCKToolbarButton('Zeit_RAW', 'Raw');
button.IconPath = FCKConfig.PageConfig.ZeitResources + '/raw/raw.png'
FCKToolbarItems.RegisterItem('Zeit_RAW', button);
