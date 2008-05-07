FCKConfig.ToolbarSets["Zeit"] = [
        ['Source', 'About'],
        ['Cut','Copy','Paste','PasteText','PasteWord'],
        ['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
        '/',
        ['FontFormat', 'Bold','Italic','Underline','StrikeThrough','-','Subscript','Superscript', 'SpecialChar'],
        ['OrderedList','UnorderedList', 'Table', 'Image', 'TextField'],
        ['Link','Unlink','Anchor'],
];

FCKConfig.SkinPath = FCKConfig.BasePath + 'skins/office2003/' ;

FCKConfig.FirefoxSpellChecker = true ;

FCKConfig.FontFormats   = 'p;h3';

FCKConfig.LinkBrowserURL = (
    FCKConfig.BasePath +
    'filemanager/browser/default/browser.html?' +
    'Connector=/@@zeit-fckeditor-link-browser.html');
FCKConfig.ImageBrowserURL = FCKConfig.LinkBrowserURL

FCKConfig.LinkUpload = false;
FCKConfig.ImageUpload = false;
FCKConfig.FlashUpload = false;
