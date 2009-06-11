FCKCommands.RegisterCommand(
    'Zeit_Pagebreak' ,
    new FCKDialogCommand(
        'Seitenumbruch', 'ZEIT: Seitenumbruch',
        FCKConfig.PageConfig.ZeitResources + '/pagebreak/dialog.pt',
        380, 250));
var button = new FCKToolbarButton('Zeit_Pagebreak', 'Seitenumbruch');
button.IconPath = FCKConfig.PageConfig.ZeitResources+'/pagebreak/icon.jpg';
FCKToolbarItems.RegisterItem('Zeit_Pagebreak', button);
