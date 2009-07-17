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
        d.addCallback(function(result) {
            return result.responseText;
        });
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
            button_placeholder_id: 'image-upload',
            prevent_swf_caching: false,
            button_text: 'Bilder hochladen',
            button_cursor : SWFUpload.CURSOR.HAND,
            button_width: 100,
            button_height: 100,
            button_image_url: self.options.resource_base_url + 
                '/upload-button.png',
            button_window_mode : SWFUpload.WINDOW_MODE.TRANSPARENT,

            file_post_name: 'form.blob',
            post_params: {
                'form.actions.add': 'Add',
            },
            file_queue_limit: 0,  // upload one at a time
            file_size_limit: 0,  // no limit
            file_types: '*.jpg;*.tif;*.gif;*.png',
            file_dialog_complete_handler: function() {
                self.files_selected();
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

    sync_and_reload: function() {
        document.location = context_url + '/@@synchronise-with-image-folder';
    },

    files_selected: function() {
        var self = this;
        // XXX handle cancel
        self.swfupload.startUpload();
        log('uploading');
    },

    upload_start: function(file) {
        var self = this;
        log("starting " + file.name);
        self.swfupload.addFileParam(file.id, 'form.__name__', file.name);
        return true;
    },

    upload_progress: function(file, uploaded, total) {
        return true;
    },

    upload_success: function(file) {
        var self = this;
        log("Uploaded " + file.name);
        return true;
    },

    upload_error: function(file, error_code, message) {
        log("ERROR ", file.name, error_code, message);
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
