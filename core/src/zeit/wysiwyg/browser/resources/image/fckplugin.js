// Plugin for adding images.

FCKCommands.RegisterCommand(
    'Zeit_Image' ,
    new FCKDialogCommand(
        'Image', 'ZEIT: Bild',
        FCKConfig.PageConfig.ZeitResources + '/image/dialog.pt',
        800, 600));


// Create the toolbar button.
var oImageItem = new FCKToolbarButton(
    'Zeit_Image', 'Image');
oImageItem.IconPath = FCKConfig.PageConfig.ZeitResources + '/image/image.gif'

FCKToolbarItems.RegisterItem('Zeit_Image', oImageItem);
        
    
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
