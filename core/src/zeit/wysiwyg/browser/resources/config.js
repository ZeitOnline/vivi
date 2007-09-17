FCKConfig.ToolbarSets["Zeit"] = [
        ['Source', 'About'],
        ['Cut','Copy','Paste','PasteText','PasteWord'],
        ['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
        '/',
        ['FontFormat', 'Bold','Italic','Underline','StrikeThrough','-','Subscript','Superscript', 'SpecialChar'],
        ['OrderedList','UnorderedList', 'Table'],
        ['Link','Unlink','Anchor'],
];

FCKConfig.SkinPath = FCKConfig.BasePath + 'skins/office2003/' ;

FCKConfig.FontFormats   = 'p;h3';

FCKConfig.LinkBrowserURL = (
    FCKConfig.BasePath +
    'filemanager/browser/default/browser.html?' +
    'Connector=/@@zeit-fckeditor-link-browser.html');


FCKConfig.LinkUpload = false;
FCKConfig.ImageUpload = false;
FCKConfig.FlashUpload = false;
