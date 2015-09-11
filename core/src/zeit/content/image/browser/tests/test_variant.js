/*global expect, describe, it, beforeEach, spyOn, afterEach, runs, waitsFor */
/*global Backbone, jQuery, zeit*/
(function ($) {
    "use strict";

    var editor_container,
        preview_container,
        setUp = function() {
            var editor, preview, variant,
                flag = false;

            // Create temporary DOM
            editor_container = $(
                '<div id="variant-inner" style="width: 220px"/>');
            preview_container = $('<div id="variant-preview"/>');
            $('body').append(editor_container);
            $('body').append(preview_container);

            // Mock AJAX calls to return hard coded response
            spyOn($, 'ajax').andCallFake(function (options) {
                var d = $.Deferred(),
                    response = {
                        focus_x: 0.5,
                        focus_y: 0.5,
                        zoom: 0.3,
                        brightness: 0.5,
                        contrast: 0.5,
                        saturation: 0.5,
                        sharpness: 0.5,
                        is_default: true,
                        url: '/fanstatic/zeit.content.image.test/master_image.jpg'
                    };
                d.resolve(response);
                options.success(response);
                return d.promise();
            });

            // Setup Editor and wait that it was rendered
            preview = new zeit.content.image.browser.VariantList();
            variant = new zeit.content.image.Variant({'id': 'square'});
            zeit.content.image.VARIANTS.add(variant);
            zeit.content.image.VARIANTS.trigger('reset');

            editor = new zeit.content.image.browser.VariantEditor();

            runs(function() {
                editor.on('render', function() {
                    flag = true;
                });
                editor.prepare();
            });

            waitsFor(function () {
                return flag;
            }, "VariantEditor did not render", 500);

            return {editor: editor, preview: preview, variant: variant};
        };

    describe("VariantEditor", function () {
        beforeEach(function() {
            var self = this,
                result = setUp();
            self.view = result.editor;
            self.preview = result.preview;
            self.variant = result.variant;
        });

        afterEach(function () {
            editor_container.remove();
            preview_container.remove();
        });

        it("should display circle relative to given focus point", function () {
            var self = this;
            runs(function() {
                expect(self.view.focuspoint.position()).toEqual({left: 110, top: 62});
            });
        });

        it("should save focus point after drag", function () {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "save").andCallThrough();
                self.view.focuspoint.css('left', '55px');
                self.view.focuspoint.css('top', '31px');
                self.view.focuspoint.trigger('dragstop');
                expect(spy).toHaveBeenCalledWith(
                    {"focus_x": 0.25, "focus_y": 0.25, "zoom": 0.3}
                );
            });
        });

        it("should display stored zoom value on load", function() {
            var self = this;
            runs(function() {
                // Since we want to inverse the default zoom-bar behaviour of
                // jqueryui, we also must expect the inverse value, i.e. 100-X
                expect(self.view.zoom_bar.slider('value')).toEqual(100 - 30);
            });
        });

        it("should store zoom value on change", function() {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "save").andCallThrough();
                // Since we want to inverse the default zoom-bar behaviour of
                // jqueryui, we also must set the inverse value, i.e. 100-X
                self.view.zoom_bar.slider('value', 100 - 60);
                self.view.zoom_bar.trigger('slidestop');
                expect(spy).toHaveBeenCalledWith(
                    {"focus_x": 0.5, "focus_y": 0.5, "zoom": 0.6}
                );
            });
        });

        it("should have 4 different image enhancements", function() {
            var self = this;
            runs(function() {
                expect(self.view.image_enhancements.length).toBe(4);
            });
        });

        it("should display value of enhancements on load", function() {
            var self = this;
            runs(function() {
                $.each(self.view.image_enhancements, function(i, name) {
                    var input = self.view[name + '_input'],
                        bar = self.view[name + '_bar'];

                    expect(input.val()).toEqual('-100');
                    expect(bar.slider("value")).toEqual(-100);
                });
            });
        });

        it("should store enhancement when changing slider", function() {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "set").andCallThrough();
                $.each(self.view.image_enhancements, function(i, name) {
                    var bar = self.view[name + '_bar'];
                    bar.slider("value", 100);
                    bar.trigger("slidestop");
                    expect(spy).toHaveBeenCalledWith(name, 1.5);
                });
            });
        });

        it("should store enhancement when changing input field", function() {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "set").andCallThrough();
                $.each(self.view.image_enhancements, function(i, name) {
                    var input_field = self.view[name + '_input'];
                    input_field.val(100);
                    input_field.trigger("blur");
                    expect(spy).toHaveBeenCalledWith(name, 1.5);
                });
            });
        });

        it("should switch back to default variant on save", function() {
            var self = this;
            runs(function() {
                self.view.switch_focus(
                    self.variant, self.preview.model_views[self.variant.id]);
                expect(self.view.current_model.id).toBe('square');
                $('input[value=Speichern]').click();
                expect(self.view.current_model.id).toBe('default');
            });
        });

        it("should switch back to default variant on delete", function() {
            var self = this;
            runs(function() {
                self.view.switch_focus(
                    self.variant, self.preview.model_views[self.variant.id]);
                expect(self.view.current_model.id).toBe('square');
                $('input[value=Verwerfen]').click();
                expect(self.view.current_model.id).toBe('default');
            });
        });

        it("should call destroy on every variant on reset", function() {
            var self = this,
                spy = spyOn(Backbone.Model.prototype, "destroy").andCallThrough();
            $("input[value='Alle Formate zurücksetzen']").click();
            expect(spy.calls.length).toEqual(1);
        });

        it("should update images of all variants on reset", function() {
            var self = this,
                image = self.preview.$('img.preview'),
                image_url = image.attr('src');
            $("input[value='Alle Formate zurücksetzen']").click();
            expect(image.attr('src')).not.toBe(image_url);
        });

        it("should update master image on save", function() {
            var self = this,
                image = self.view.$('img.editor'),
                image_url = image.attr('src');
            self.view.save();
            expect(image.attr('src')).not.toBe(image_url);
        });
    });
}(jQuery));
