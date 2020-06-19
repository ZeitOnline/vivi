(function($) {
  $(document).bind('fragment-ready', function() {
    $('.block.type-citation_comment input[name$="url"]').bind('paste', function(e) {
      var id = $(this).context.id.split('.')[1];
      var env_url = $(this).context.dataset.environment;
      pasted_url = e.originalEvent.clipboardData.getData('text/plain');
      var cid = pasted_url.split('#')[1].replace('cid-', '');
      var comments_api_endpoint = env_url+"/comments?id=eq."+cid;
      $.getJSON(comments_api_endpoint)
      .done(function(data){
        var comment = $(data[0]['content']).text();
        $('#citationcomment\\.'+id+'\\.text').val(comment);
      })
      .fail(function(jqxhr, textStatus, error){
        $('#citationcomment\\.'+id+'\\.text').val('FEHLER: Kommentar konnte nicht geladen werden!\n'+comments_api_endpoint+' nicht erreichbar? Falsche cid?');
        var err = textStatus + ", " + error;
        console.log( "Request Failed: " + err );
      });
    });
  });
})(jQuery);
