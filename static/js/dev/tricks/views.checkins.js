/* 
 * triks.views.checkins
 *
 * All about checkins views
 * :copyright: (c) 2013 by zero13cool
 */

Besttrick.module('Tricks.Views', function (Views, App, Backbone, Marionette, $, _) {
    Views.Checkins = App.Common.ItemsView.extend({
        get_left_side: function (model) {
            return model.get('cones');
        },
        get_left_side_two: function (model) {
            if (model.get('video_url') && model.get('approved') === 1) {
                return '<a class="has_video video_approved" href="'+model.get('video_url')+'" target="_blank" title="есть видео подтверждение">\
                            <i class="icon-facetime-video"></i>\
                        </a>'
            }
            return ''    
        },
        get_middle_side_content: function (model) {
            return {
                href: model.get('user').get_profile_url(),
                title: model.get('user').get('nick')
            }
        },
        get_middle_side_hint: function (model) {},
        get_right_side: function (model) {
            return '<img width="50" src="' + model.get('user').get("photo") + '" />';
        }
    });

    Views.CheckinForm = Backbone.Form.extend({
        className: 'trick__dialog',

        events: {
            'click a.dialog__close i': 'close',
            'click a.dialog__save': 'save'
        },

        render: function (args) {
            Backbone.Form.prototype.render.call(this, args);
            this.trigger('after:render');
   
            this.$el.find('input')
                .tooltip({trigger: 'focus'})
                .errortip({trigger: 'manual'});

            return this;
        },

        initialize: function (args) {
            Backbone.Form.prototype.initialize.call(this, args);
            this.parent_view = args.parent;

            // this.model.on('change', function () {
            //     this.model.save();
            //     this.render()
            // }, this);

            this.on('after:render', function () {
                var w = args.parent.$el.width(),
                    h = args.parent.$el.height();
                this.$el.width(w+2).height(h-21);
            }, this);
        },

        save: function () {
            var self = this,
                errors = this.commit();

            if (errors) {
                _.each(errors, function (k, v) {
                    self.fields[v].editor.$el.addClass('error')
                        .tooltip('disable').errortip('enable').errortip('show')
                        .one('blur, keydown', function () {
                            $(this).errortip('hide').errortip('disable').tooltip('enable');
                        });
                });
                return false;
            }

            if (this.model.hasChanged()) {
                this.model.save();
                this.close();
                this.parent_view.model.trigger('change');
                return false;
            }
        },

        close: function () {
            $('div.tooltip').remove();
            this.remove();
            return false;
        }
    });
});
