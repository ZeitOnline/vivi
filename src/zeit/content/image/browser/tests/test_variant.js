/*global expect, describe, it, beforeEach, spyOn, afterEach, runs, waitsFor */
/*global Backbone, jQuery, zeit*/
(function ($) {
    "use strict";

    describe("Focuspoint Test", function () {
        beforeEach(function() {
            var self = this,
                flag = false;

            // Create temporary DOM
            this.container = $('<div id="variant-inner" style="width: 220px"/>');
            $('body').append(this.container);

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
            self.view = new zeit.content.image.browser.VariantEditor();

            runs(function() {
                self.view.on('render', function() {
                    flag = true;
                });
                self.view.prepare();
            });

            waitsFor(function () {
                return flag;
            }, "VariantEditor did not render", 500);
        });

        afterEach(function () {
            this.container.remove();
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

        // ===================== Brightness =====================
        it("should display stored brightness value on load", function() {
            var self = this;
            runs(function() {
                expect(self.view.brightness_bar.slider('value')).toEqual(-100);
                expect(self.view.brightness_input.val()).toEqual('-100');
            });
        });

        it("should store brightness value when changing slider", function() {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "set").andCallThrough();
                self.view.brightness_bar.slider('value', 100);
                self.view.brightness_bar.trigger('slidestop');
                expect(spy).toHaveBeenCalledWith("brightness", 1.5);
            });
        });

        it("should store brightness value when changing input field", function() {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "set").andCallThrough();
                self.view.brightness_input.val(100);
                self.view.brightness_input.trigger('blur');
                expect(spy).toHaveBeenCalledWith("brightness", 1.5);
            });
        });

        // ===================== Contrast =====================
        it("should display stored contrast value on load", function() {
            var self = this;
            runs(function() {
                expect(self.view.contrast_bar.slider('value')).toEqual(-100);
                expect(self.view.contrast_input.val()).toEqual('-100');
            });
        });

        it("should store contrast value when changing slider", function() {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "set").andCallThrough();
                self.view.contrast_bar.slider('value', 100);
                self.view.contrast_bar.trigger('slidestop');
                expect(spy).toHaveBeenCalledWith("contrast", 1.5);
            });
        });

        it("should store contrast value when changing input field", function() {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "set").andCallThrough();
                self.view.contrast_input.val(100);
                self.view.contrast_input.trigger('blur');
                expect(spy).toHaveBeenCalledWith("contrast", 1.5);
            });
        });

        // ===================== Saturation =====================
        it("should display stored saturation value on load", function() {
            var self = this;
            runs(function() {
                expect(self.view.saturation_bar.slider('value')).toEqual(-100);
                expect(self.view.saturation_input.val()).toEqual('-100');
            });
        });

        it("should store saturation value when changing slider", function() {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "set").andCallThrough();
                self.view.saturation_bar.slider('value', 100);
                self.view.saturation_bar.trigger('slidestop');
                expect(spy).toHaveBeenCalledWith("saturation", 1.5);
            });
        });

        it("should store saturation value when changing input field", function() {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "set").andCallThrough();
                self.view.saturation_input.val(100);
                self.view.saturation_input.trigger('blur');
                expect(spy).toHaveBeenCalledWith("saturation", 1.5);
            });
        });

        // ===================== Sharpness =====================
        it("should display stored sharpness value on load", function() {
            var self = this;
            runs(function() {
                expect(self.view.sharpness_bar.slider('value')).toEqual(-100);
                expect(self.view.sharpness_input.val()).toEqual('-100');
            });
        });

        it("should store sharpness value when changing slider", function() {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "set").andCallThrough();
                self.view.sharpness_bar.slider('value', 100);
                self.view.sharpness_bar.trigger('slidestop');
                expect(spy).toHaveBeenCalledWith("sharpness", 1.5);
            });
        });

        it("should store sharpness value when changing input field", function() {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "set").andCallThrough();
                self.view.sharpness_input.val(100);
                self.view.sharpness_input.trigger('blur');
                expect(spy).toHaveBeenCalledWith("sharpness", 1.5);
            });
        });
    });


    describe("Button Test", function () {
        beforeEach(function() {
            var self = this,
                flag = false;

            // Create temporary DOM
            this.editor_container = $(
                '<div id="variant-inner" style="width: 220px"/>');
            this.preview_container = $('<div id="variant-preview"/>');
            $('body').append(this.editor_container);
            $('body').append(this.preview_container);

            // Mock AJAX calls to return hard coded response
            spyOn($, 'ajax').andCallFake(function (options) {
                var d = $.Deferred(), response = {
                    is_default: true,
                    url: '/fanstatic/zeit.content.image.test/master_image.jpg'
                };
                d.resolve(response);
                options.success(response);
                return d.promise();
            });

            // Setup Editor and wait that it was rendered
            self.preview = new zeit.content.image.browser.VariantList();
            self.variant = new zeit.content.image.Variant({'id': 'square'});
            zeit.content.image.VARIANTS.add(self.variant);
            zeit.content.image.VARIANTS.trigger('reset');

            self.view = new zeit.content.image.browser.VariantEditor();

            runs(function() {
                self.view.on('render', function() {
                    flag = true;
                });
                self.view.prepare();
            });

            waitsFor(function () {
                return flag;
            }, "VariantEditor did not render", 500);
        });

        afterEach(function () {
            this.editor_container.remove();
            this.preview_container.remove();
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
                image = self.preview_container.find('img.preview'),
                image_url = image.attr('src');
            $("input[value='Alle Formate zurücksetzen']").click();
            expect(image.attr('src')).not.toBe(image_url);
        });

        it("should update master image on save", function() {
            var self = this,
                image = self.editor_container.find('img.editor'),
                image_url = image.attr('src');
            self.view.save();
            expect(image.attr('src')).not.toBe(image_url);
        });
    });
}(jQuery));
