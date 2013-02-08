FCKConfig.ToolbarSets["Zeit"] = [
        ['Source', 'About'],
        ['Cut','Copy','Paste','PasteText','PasteWord'],
        ['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
        ['Link','Unlink'],
        '/',
        ['FontFormat', 'Bold','Italic','Underline','StrikeThrough','-','Subscript','Superscript', 'SpecialChar'],
        ['OrderedList','UnorderedList'],
        ['Zeit_Image', 'Zeit_Add_Video', 'Zeit_Add_Audio',
         'Zeit_RAW', 'Zeit_Pagebreak',
         'Zeit_Infobox', 'Zeit_Portraitbox', 'Zeit_Gallery', 'Zeit_Citation',
         'Zeit_Related', 'Zeit_Timeline'],
];

FCKConfig.SkinPath = FCKConfig.BasePath + 'skins/office2003/' ;

FCKConfig.FirefoxSpellChecker = true ;

FCKConfig.FontFormats = 'p;h3';

FCKConfig.LinkBrowserURL = (
    FCKConfig.BasePath +
    'filemanager/browser/default/browser.html?' +
    'Connector='
    + FCKConfig.BasePath + '../../../@@zeit-fckeditor-link-browser.html');
FCKConfig.ImageBrowserURL = FCKConfig.LinkBrowserURL

FCKConfig.LinkUpload = false;
FCKConfig.ImageUpload = false;
FCKConfig.FlashUpload = false;

var plugins = [
    'citation',
    'pagebreak',
    'raw',
    'reference',
    'related',
    'video',
];

for (var i = 0 ; i < plugins.length; i++) {
    var plugin = plugins[i];
    FCKConfig.Plugins.Add(plugin, '', FCKConfig.PageConfig.ZeitResources + '/');
}


FCK.CustomCleanWord = function( oNode, bIgnoreFont, bRemoveStyles )
{
    var html = CleanWord(oNode, bIgnoreFont, bRemoveStyles);
    if (html.indexOf('<p>') == -1) {
        // If there is *no* paragraph, change normal breaks to paragraphs.
        html = '<p>' + html.replace(/<br>/g, '</p><p>') + '</p>';
    }
    return html;
};


// I *really* hate that I cannot reference the original function from
// fck_paste.js
function CleanWord( oNode, bIgnoreFont, bRemoveStyles )
{
    // Remove some common nodes from the top level

    var to_delete = oNode.ownerDocument.evaluate(
        '//META|//LINK|//STYLE',
        oNode, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);

    for (var i=0 ; i < to_delete.snapshotLength; i++) {
        var node = to_delete.snapshotItem(i);
        node.parentNode.removeChild(node);
    }

    // Remove everything but elements and text
    var next = oNode.firstChild;
    while (next) {
        var node = next;
        next = node.nextSibling;

        if (node.nodeType == node.TEXT_NODE)
            continue
        if (node.nodeType == node.ELEMENT_NODE)
            continue

        node.parentNode.removeChild(node);
    }

    var html = oNode.innerHTML ;

    html = html.replace(/<o:p>\s*<\/o:p>/g, '') ;
    html = html.replace(/<o:p>.*?<\/o:p>/g, '') ;

    // Remove mso-xxx styles.
    html = html.replace( /\s*mso-[^:]+:[^;"]+;?/gi, '' ) ;

    // Remove margin styles.
    html = html.replace( /\s*MARGIN: 0cm 0cm 0pt\s*;/gi, '' ) ;
    html = html.replace( /\s*MARGIN: 0cm 0cm 0pt\s*"/gi, "\"" ) ;

    html = html.replace( /\s*TEXT-INDENT: 0cm\s*;/gi, '' ) ;
    html = html.replace( /\s*TEXT-INDENT: 0cm\s*"/gi, "\"" ) ;

    html = html.replace( /\s*TEXT-ALIGN: [^\s;]+;?"/gi, "\"" ) ;

    html = html.replace( /\s*PAGE-BREAK-BEFORE: [^\s;]+;?"/gi, "\"" ) ;

    html = html.replace( /\s*FONT-VARIANT: [^\s;]+;?"/gi, "\"" ) ;

    html = html.replace( /\s*tab-stops:[^;"]*;?/gi, '' ) ;
    html = html.replace( /\s*tab-stops:[^"]*/gi, '' ) ;

    // Remove FONT face attributes.
    if ( bIgnoreFont )
    {
        html = html.replace( /\s*face="[^"]*"/gi, '' ) ;
        html = html.replace( /\s*face=[^ >]*/gi, '' ) ;

        html = html.replace( /\s*FONT-FAMILY:[^;"]*;?/gi, '' ) ;
    }

    // Remove Class attributes
    html = html.replace(/<(\w[^>]*) class=([^ |>]*)([^>]*)/gi, "<$1$3") ;

    // Remove styles.
    if ( bRemoveStyles )
        html = html.replace( /<(\w[^>]*) style="([^\"]*)"([^>]*)/gi, "<$1$3" ) ;

    // Remove empty styles.
    html =  html.replace( /\s*style="\s*"/gi, '' ) ;

    html = html.replace( /<SPAN\s*[^>]*>\s*&nbsp;\s*<\/SPAN>/gi, '&nbsp;' ) ;

    html = html.replace( /<SPAN\s*[^>]*><\/SPAN>/gi, '' ) ;

    // Remove Lang attributes
    html = html.replace(/<(\w[^>]*) lang=([^ |>]*)([^>]*)/gi, "<$1$3") ;

    html = html.replace( /<SPAN\s*>(.*?)<\/SPAN>/gi, '$1' ) ;

    html = html.replace( /<FONT\s*>(.*?)<\/FONT>/gi, '$1' ) ;

    // Remove XML elements and declarations
    html = html.replace(/<\\?\?xml[^>]*>/gi, '' ) ;

    // Remove Tags with XML namespace declarations: <o:p><\/o:p>
    html = html.replace(/<\/?\w+:[^>]*>/gi, '' ) ;

    // Remove comments [SF BUG-1481861].
    html = html.replace(/<\!--.*?-->/g, '' ) ;

    html = html.replace( /<(U|I|STRIKE)>&nbsp;<\/\1>/g, '&nbsp;' ) ;

    html = html.replace( /<H\d>\s*<\/H\d>/gi, '' ) ;

    // Remove "display:none" tags.
    html = html.replace( /<(\w+)[^>]*\sstyle="[^"]*DISPLAY\s?:\s?none(.*?)<\/\1>/ig, '' ) ;

    // Remove language tags
    html = html.replace( /<(\w[^>]*) language=([^ |>]*)([^>]*)/gi, "<$1$3") ;

    // Remove onmouseover and onmouseout events (from MS Word comments effect)
    html = html.replace( /<(\w[^>]*) onmouseover="([^\"]*)"([^>]*)/gi, "<$1$3") ;
    html = html.replace( /<(\w[^>]*) onmouseout="([^\"]*)"([^>]*)/gi, "<$1$3") ;

    // The original <Hn> tag send from Word is something like this: <Hn style="margin-top:0px;margin-bottom:0px">
    html = html.replace( /<H(\d)([^>]*)>/gi, '<h$1>' ) ;

    // Word likes to insert extra <font> tags, when using MSIE. (Wierd).
    html = html.replace( /<(H\d)><FONT[^>]*>(.*?)<\/FONT><\/\1>/gi, '<$1>$2<\/$1>' );
    html = html.replace( /<(H\d)><EM>(.*?)<\/EM><\/\1>/gi, '<$1>$2<\/$1>' );

    // Remove empty tags (three times, just to be sure).
    // This also removes any empty anchor
    html = html.replace( /<([^\s>]+)(\s[^>]*)?>\s*<\/\1>/g, '' ) ;
    html = html.replace( /<([^\s>]+)(\s[^>]*)?>\s*<\/\1>/g, '' ) ;
    html = html.replace( /<([^\s>]+)(\s[^>]*)?>\s*<\/\1>/g, '' ) ;

    return html ;
}
