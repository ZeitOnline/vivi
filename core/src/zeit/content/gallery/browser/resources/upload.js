zeit.cms.declare_namespace('zeit.content.gallery');

zeit.content.gallery.Uploader = gocept.Class.extend({

    construct: function(options) {
        var self = this;
        self.options = options;
        var d = self.get_ticket()
        d.addCallback(function(ticket) {
            self.init_uploader(ticket);
        });
    },

    get_ticket: function() {
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            application_url + '/@@get-ticket');
        d.addCallbacks(function(result) {
            return result.responseText;
        },
        zeit.cms.log_error);
        return d;
    },

    get_upload_url: function(ticket) {
        var context = context_url.substr(application_url.length);
        var url = application_url + '/++ticket++' + ticket + context + 
            '/@@upload-image';
        return url;
    },

    init_uploader: function(ticket) {
        var self = this;
        self.swfupload = new SWFUpload({
            flash_url: self.options.resource_base_url 
                  + '/SWFUpload/Flash/swfupload.swf',
            upload_url: self.get_upload_url(ticket),
            http_success: [201],
            button_placeholder_id: 'image-upload',
            prevent_swf_caching: false,
            button_cursor : SWFUpload.CURSOR.HAND,
            button_width: 200,
            button_height: 18,
	    button_text: 'Bilder hochladen',
	    button_text_left_padding: 40,
            button_image_url: self.options.resource_base_url + 
                '/upload-icon.png',
            button_window_mode : SWFUpload.WINDOW_MODE.TRANSPARENT,

            file_post_name: 'form.blob',
            post_params: {
                'form.actions.add': 'Add',
            },
            file_queue_limit: 0,  // no limit
            file_size_limit: 0,  // no limit
            file_types: '*.jpg;*.tif;*.gif;*.png',
            file_dialog_start_handler: function() {
                self.file_dialog_start();
            },
            file_queued_handler: function(file) {
                self.file_queued(file);
            },
            file_dialog_complete_handler: function(
                selected, queued, total_queued) {
                self.file_dialog_complete(selected, queued, total_queued);
            },
            upload_start_handler: function(file) {
                self.upload_start(file);
            },
            upload_progress_handler: function(file, uploaded, total) {
                self.upload_progress(file, uploaded, total);
            },
            upload_success_handler: function(file) {
                self.upload_success(file);
            },
            upload_error_handler: function(file, error_code, message) {
                self.upload_error(file, error_code, message);
            },
            upload_complete_handler: function(file) {
                self.upload_complete(file);
            },
        });
    },

    get_id: function(file) {
        return 'file-' + file.id;
    },
    
    set_progress: function(file, progress) {
        var self = this;
        var div = $(self.get_id(file));
        var progress_div = MochiKit.DOM.getFirstElementByTagAndClassName(
            'div', 'progress', div);
        progress_div.innerHTML = progress;
    },

    make_active: function(file) {
        var self = this;
        var divs = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'upload', self.lightbox.content_box);
        forEach(divs, function(div) {
            MochiKit.DOM.removeElementClass(div, 'busy');
        });
        if (!isUndefinedOrNull(file)) {
            MochiKit.DOM.addElementClass($(self.get_id(file)), 'busy');
        }
    },

    sync_and_reload: function() {
        var self = this;
        self.make_active(null);
        self.lightbox.content_box.appendChild(
            DIV({'class': 'upload busy'},
                DIV({'class': 'filename'},
                    "Creating thumbnails and reloading …")));
        // We're making another async call here because the synchronize takes a
        // while. When we'd set document.location immeadiately the animated
        // busy indicator would stop until everything is processes.
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            context_url + '/@@synchronise-with-image-folder?redirect=false');
        d.addCallbacks(function(result) {
            document.location = result.responseText;
        },
        zeit.cms.log_error);
    },

    file_dialog_start: function() {
        var self = this;
        self.lightbox = new gocept.Lightbox(jQuery('body')[0]);
        self.lightbox.content_box.appendChild(
            H1({}, "Uploading images …"));
        return true;
    },

    file_queued: function(file) {
        var self = this;
        var id = self.get_id(file);
        var filename_contents = file.name + ' (' + file.size + ' Bytes)';
        self.lightbox.content_box.appendChild(
            DIV({'id': id, 'class': 'upload'}, 
                DIV({'class': 'filename'}, filename_contents),
                DIV({'class': 'progress'}, '0')));
        return true;
    },

    file_dialog_complete: function(selected, queued, total_queued) {
        var self = this;
        if (selected) {
            self.swfupload.startUpload();
        } else {
            self.lightbox.close();
        }
    },

    upload_start: function(file) {
        var self = this;
        self.swfupload.addFileParam(file.id, 'form.__name__', file.name);
        self.make_active(file);
        return true;
    },

    upload_progress: function(file, uploaded, total) {
        var self = this;
        self.set_progress(file, Math.ceil(uploaded/total*100));
        return true;
    },

    upload_success: function(file) {
        var self = this;
        self.set_progress(file, 100);
        return true;
    },

    upload_error: function(file, error_code, message) {
        var self = this;
        self.set_progress(file, 'ERR');
        logError(message, error_code);
        return true;
    },

    upload_complete: function(file) {
        var self = this;
        var stats = self.swfupload.getStats();
        if (stats.files_queued) {
            self.swfupload.startUpload();
        } else {
            self.sync_and_reload();
        }
        return true;
    },
});
