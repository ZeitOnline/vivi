FCKCommands.RegisterCommand(
    'Zeit_Image' ,
    new FCKDialogCommand(
        'Image', 'ZEIT: Bild',
        FCKConfig.PageConfig.ZeitResources + '/reference/image.pt',
        800, 600));
var button = new FCKToolbarButton('Zeit_Image', 'Image');
button.IconPath = FCKConfig.PageConfig.ZeitResources + '/reference/image.gif'
FCKToolbarItems.RegisterItem('Zeit_Image', button);


// Register context menu item
FCK.ContextMenu.RegisterListener({
    AddItems : function(menu, element, tagName) {
        if (tagName != 'IMG')
            return;
        // when the option is displayed, show a separator  the command
        menu.AddSeparator() ;
        // the command needs the registered command name, the title for the
        // context menu, and the icon path
        menu.AddItem(
            'Zeit_Image',
            'Bild ändern',
            oImageItem.IconPath);
    }
});
