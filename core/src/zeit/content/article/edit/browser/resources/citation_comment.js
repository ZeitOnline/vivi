( function( $ ) {
    $( document ).bind( 'fragment-ready', function( event ) {
        var target = event.__target;

        // beware of target being window or document, not implementing Element.closest()
        // use optional chaining - it's 2020
        if ( !target?.closest?.( '.block.type-citation_comment' ) ) {
            return;
        }

        var element = target.querySelector( 'input[name$="url"]' );

        if ( !element ) {
            return;
        }

        element.addEventListener( 'input', function() {
            var textareaId = this.name.replace( /url$/, 'text' );
            var textarea = this.form.elements[ textareaId ];
            var commentsApiUrl = this.dataset.commentsApiUrl;
            var cid = null;

            if ( !this.value ) {
                textarea.value = '';
                return;
            }

            try {
                var commentUrl = new URL( this.value );
                if ( commentUrl.searchParams.has( 'cid' ) ) {
                    // check query string parameter
                    cid = commentUrl.searchParams.get( 'cid' );
                } else if ( commentUrl.hash ) {
                    // check url fragment
                    cid = commentUrl.hash.replace( '#cid-', '' );
                }
            } catch ( error ) {
                console.error( error );
            }

            if (commentsApiUrl  && cid && textarea ) {
                var url = `${commentsApiUrl}/comments?id=eq.${cid}`;

                fetch( url ).then( function( response ) {
                    return response.json();
                }).then( function( data ) {
                    if ( data && data.length ) {
                        textarea.value = data[ 0 ].content;
                    } else {
                        throw new Error( 'Empty result' );
                    }
                }).catch( function( error ) {
                    textarea.value = `FEHLER: Kommentar konnte nicht geladen werden!\n${commentsApiUrl} nicht erreichbar?\nFalsche Kommentar ID? (${cid})`;
                });
            }
        });
    });
})( jQuery );
