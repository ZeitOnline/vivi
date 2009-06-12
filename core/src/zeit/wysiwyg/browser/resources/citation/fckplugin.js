FCKCommands.RegisterCommand(
    'Zeit_Citation' ,
    new FCKDialogCommand(
        'Zitat', 'ZEIT: Zitat',
        FCKConfig.PageConfig.ZeitResources + '/citation/dialog.pt',
        380, 350));
var button = new FCKToolbarButton('Zeit_Citation', 'Zitat');
button.IconPath = FCKConfig.PageConfig.ZeitResources+'/citation/icon.jpg';
FCKToolbarItems.RegisterItem('Zeit_Citation', button);
