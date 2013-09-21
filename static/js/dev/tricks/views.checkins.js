/* 
 * triks.views.checkins
 *
 * All about checkins views
 * :copyright: (c) 2013 by zero13cool
 */

Besttrick.module('Tricks.Views', function (Views, App, Backbone, Marionette, $, _) {
  Views.Checkins = App.Common.ItemsView.extend({
    empty_text: 'Еще никто не делает этот трюк',

    get_left_side: function (model) {
      return model.get('cones');
    },

    get_left_side_two: function (model) {
      if (model.get('video_url') && model.get('approved') === 1) {
        return '<a class="has_video video_approved" href="'+model.get('video_url')+'" target="_blank" title="есть видео подтверждение">\
                  <i class="icon-facetime-video"></i>\
                </a>'
        }
        return '';
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
      'click a.dialog__save': 'save',
      'click a.upload_video_link': 'show_upload_video_form'
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

      this.on('after:render', function () {
        var w = args.parent.$el.width(),
            h = args.parent.$el.height();
        this.$el.width(w+2).height(h-21);
      }, this);
    },

    show_error: function (field, error_text) {
      var $el = this.fields[field].editor.$el;
          $el.data('error-title', error_text)

      $el.addClass('error')
        .tooltip('disable').errortip('enable')
        .errortip('show')
        .one('blur, change', function () {
            $(this).errortip('hide').errortip('disable').tooltip('enable')
                   .removeClass('error').data('error-title', null);
        });
      },

    save: function () {
      var self = this,
          errors = this.commit();

      if (errors) {
        _.each(errors, function (k, v) {
            self.show_error(v);
        });
        return false;
      }

      if (this.model.hasChanged()) {
        this.model.save(null, {
          success: function () {
            console.log('success');
            self.close();
            // self.parent_view.model.trigger('change');
            self.parent_view.model.fetch();
          },
          error: function (model, response) {
            var error = JSON.parse(response.responseText);
            console.log(error);
            self.show_error(error.field, error.text);
          }
        });
      }
      return false;
    },

    close: function () {
      $('div.tooltip').remove();
      this.remove();
      return false;
    },

    show_upload_video_form: function () {
      var upload_form = new Views.UploadVideoForm({
        trick_id: this.parent_view.model.get('id'),
        parent_view: this
      });
      App.modal.show(upload_form);
      return false;
    }
  });
});
