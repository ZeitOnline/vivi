FCKCommands.RegisterCommand(
    'Zeit_Citation' ,
    new FCKDialogCommand(
        'Zitat', 'ZEIT: Zitat',
        FCKConfig.PageConfig.ZeitResources + '/citation/dialog.pt',
        800, 600));
var button = new FCKToolbarButton('Zeit_Citation', 'Zitat');
button.IconPath = FCKConfig.PageConfig.ZeitResources+'/citation/icon.png';
FCKToolbarItems.RegisterItem('Zeit_Citation', button);
