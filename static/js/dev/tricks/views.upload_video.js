/*
 * Form for upload video to YouTube
 */
Besttrick.module('Tricks.Views', function (Views, App, Backbone, Marionette, $, _) {
  Views.UploadVideoForm = App.Common.ModalView.extend({
    className: 'upload_video_form_container',

    events: function () {
      return _.extend({}, App.Common.ModalView.prototype.events, {
        'click input[type=checkbox]': 'toggle_upload_button'
      });
    },

    initialize: function (options) {
      App.Common.ModalView.prototype.initialize.call(this);
      // do this async!
      this.youtube_params = this.get_youtube_params(options.trick_id);
      this.parent_view = options.parent_view;

      this.on('render', this.init_form, this);
    },

    init_form: function () {
      var self = this;

      this.form = this.$el.find('form').ajaxForm({
        iframe: true, // так как ютуб использует редирект, нам нужно прогрузить его через iframe
        dataType: 'json',

        beforeSubmit: function (arr, form, options) {
          var form_valid = false;

          _.each(arr, function (el, i) {
            if (el.name === "file" && el.value.size && /video/.test(el.value.type))  {
              form_valid = true;
            }
          });

          if (!form_valid) {
            self.show_error('Некорретно заполнена форма');
            return false;
          }

          // валидация пройдена, дисайблим кнопку, показываем лоадер, все дела
          self._disable_button(form.find('button'));
          form.find('div.upload_form__loader').show();

          return true;
        },

        complete: function (xhr) {
          var response = JSON.parse(xhr.responseText),
              video_id;

          if (response.status[0] !== '200') {
            alert('Ошибка загрузки видео со стороны YouTube.');
            self._enable_button(form.find('button'));
            return;
          }

          video_id = response.id[0];
          self.parent_view.setValue('video_url', 'http://youtu.be/' + video_id);
          self.close();
        }
      });
    },

    mixinTemplateHelpers: function () {
      return this.youtube_params;
    },

    toggle_upload_button: function (e) {
      var $el = $(e.target),
          button = $(this.$el.find('button[type="submit"]')[0]);

      $el.is(':checked') ? this._enable_button(button) : this._disable_button(button);
    },

    _enable_button: function (b) {
      b.removeClass('disabled').attr('disabled', null);
    },

    _disable_button: function (b) {
      b.addClass('disabled').attr('disabled', 'disabled');
    },

    show_error: function (text) {
      var tmpl = '\
        <div class="notice error">\
          <i class="icon-remove-sign icon-large"></i>\
          <%= text %>\
          <a href="#close" class="icon-remove"></a>\
        </div>\
      ';

      this.form.append(_.template(tmpl, {'text': text}));
    },

    get_youtube_params: function (trick_id) {
      var self = this,
          params = false;
      
      $.ajax({
        url: '/prepare_youtube_upload/',
        data: {'trick_id': trick_id},
        dataType: 'json',
        async: false,

        success: function (response) {
          params = response;
        },
        error: function () {
          self.show_error('Внутренняя ошибка сервера.');
        }
      });

      return params;
    }
  });
});
