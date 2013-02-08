FCKCommands.RegisterCommand(
    'Zeit_Image' ,
    new FCKDialogCommand(
        'Image', 'ZEIT: Bild',
        FCKConfig.PageConfig.ZeitResources + '/reference/image.pt',
        800, 600));
var image_button = new FCKToolbarButton('Zeit_Image', 'Image');
image_button.IconPath = FCKConfig.PageConfig.ZeitResources + '/reference/image.gif'
FCKToolbarItems.RegisterItem('Zeit_Image', image_button);


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
            image_button.IconPath);
    }
});


FCKCommands.RegisterCommand(
    'Zeit_Infobox' ,
    new FCKDialogCommand(
        'Infobox', 'ZEIT: Infobox',
        FCKConfig.PageConfig.ZeitResources + '/reference/infobox.pt',
        800, 600));
var button = new FCKToolbarButton('Zeit_Infobox', 'Infobox');
button.IconPath = FCKConfig.PageConfig.ZeitResources + '/reference/infobox.png'
FCKToolbarItems.RegisterItem('Zeit_Infobox', button);


FCKCommands.RegisterCommand(
    'Zeit_Timeline' ,
    new FCKDialogCommand(
        'Timeline', 'ZEIT: Zeitstrahl',
        FCKConfig.PageConfig.ZeitResources + '/reference/timeline.pt',
        800, 600));
var button = new FCKToolbarButton('Zeit_Timeline', 'Zeitstrahl');
button.IconPath = FCKConfig.PageConfig.ZeitResources + '/reference/timeline.png'
FCKToolbarItems.RegisterItem('Zeit_Timeline', button);


FCKCommands.RegisterCommand(
    'Zeit_Portraitbox' ,
    new FCKDialogCommand(
        'Portraitbox', 'ZEIT: Porträtbox',
        FCKConfig.PageConfig.ZeitResources + '/reference/portraitbox.pt',
        800, 600));
var button = new FCKToolbarButton('Zeit_Portraitbox', 'Portraitbox');
button.IconPath = FCKConfig.PageConfig.ZeitResources +
    '/reference/portraitbox.png'
FCKToolbarItems.RegisterItem('Zeit_Portraitbox', button);


FCKCommands.RegisterCommand(
    'Zeit_Gallery' ,
    new FCKDialogCommand(
        'Gallery', 'ZEIT: Bildergalerie',
        FCKConfig.PageConfig.ZeitResources + '/reference/gallery.pt',
        800, 600));
var button = new FCKToolbarButton('Zeit_Gallery', 'Gallery');
button.IconPath = FCKConfig.PageConfig.ZeitResources + '/reference/gallery.png'
FCKToolbarItems.RegisterItem('Zeit_Gallery', button);
