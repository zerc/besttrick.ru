/*
 * Common functions, hooks, cheets and other uncategoried stuff
 */

Besttrick.module('Common', function (Common, App, Backbone, Marionette, $, _) {
    Common.Vars = {
        // кука в которую сохраняется url страницы с которой логинились 
        // (туда будет выполнен редирект после логина)
        next_url_cookie_name: 'next',

        // имя куки для сохранения данных чекина навторизованного пользователя
        tmp_trick_cookie_name: 'trick'
    },

    Common.Functions = {
        plural: function(number, one, two, five) {
            var n = Math.abs(number);

            n %= 100;
            if (n >= 5 && n <= 20) return number + ' ' + five;

            n %= 10;
            if (n == 1) return number + ' ' + one;

            if (n >= 2 && n <= 4) return number + ' ' + two;

            return number + ' ' + five;
        },

        render_video_thumb: function (video_url, title) {
            var thumb_url = this.get_youtube_video_id(video_url);
            return '<img src="http://img.youtube.com/vi/'+thumb_url+'/1.jpg" alt="'+title+'" height="50" />';
        },

        get_youtube_video_id: function (video_url) {
            if (/embed|youtu\.be/.test(video_url)) return video_url.split('/').pop();
            if (/\/watch\?v=/.test(video_url)) return /\?v=([^&]+)/.exec(video_url).pop();
            if (/img.youtube.com/.test(video_url)) return /vi\/([^&]+)\//.exec(video_url).pop();
            throw "Can't parse video_url string!";
        }
    };

    Common.Model = Backbone.Model.extend({
        wrappers: {},
        props: [],
        methods: [],

        // TODO: do this better >_>
        _self_extend: function (obj) {
            _.each(this.props, function (p) {
                obj[p.split('get_').pop()] = this[p]();
            }, this);

            _.each(this.methods, function (p) {
                obj[p] = this[p];
            }, this);
        },

        initialize: function () {
            _.each(this.wrappers, function (w, k) {
                this.set(k, _.isEmpty(this.get(k)) ? false : new w(this.get(k)));
            }, this);
        },

        toJSON: function() {
            var attrs = Backbone.Model.prototype.toJSON.call(this);            
            this._self_extend(attrs)
            return attrs;
        }
    });

    Common.ItemsView = Marionette.ItemView.extend({
        // TODO: add dom elements constructors: make_img({src:asda.jpg, title:adaa}), make_link
        template: '#items',
        tagName: 'table',
        className: 'items',
        empty_text: 'Нет элементов для отображения',

        serializeData: function(){
            var data = {
                extra_class: '',
                show_first: true,
                empty_text: this.empty_text
            };

            data.items = this.collection.map(function (item) {
                return {
                    left_side: this.get_left_side(item),
                    left_side_two: this.get_left_side_two(item),
                    middle_side_content: this.get_middle_side_content(item),
                    middle_side_hint: this.get_middle_side_hint(item),
                    right_side: this.get_right_side(item)
                }
            }, this);

            _.extend(data, this.options, this.extras);

            return data;
        },

        get_left_side: function (model) {},
        get_left_side_two: function (model) {},
        get_middle_side_content: function (model) {},
        get_middle_side_hint: function (model) {},
        get_right_side: function (model) {},

        extras: {
            right_side_class: ' icon-user icon-2x'
        }
    });

    Common.init_feedback = function (opts, user) {
        var $control = opts.control;
        $control.tooltip(opts);

        // repair this bug. Dont work click event on control element!
        $control.toggle(
            function () { $(this).tooltip('show'); },
            function () { $(this).tooltip('hide'); }
        )

        App.send_feedback = function (form) {
            var success_html = '\
                <div class="success clearfix">\
                    <i class="icon-ok-circle icon-large pull-left"></i>\
                    Ваш отзыв успешно отправлен.\
                </div>',
                error_html = '\
                <div class="error clearfix">\
                    <i class="icon-ban-circle icon-large pull-left"></i>\
                    Произошла непредвиденная ошибка.\
                </div>',
                data = {},
                errors = 0;

            _.map(form.find('input, textarea'), function (el) {
                var $el = $(el);
                if (!$el.val()) {
                    $el.addClass('error');
                } else {
                    data[$el.attr('id')] = $el.val();
                    $el.removeClass('error');
                }
            });

            if (form.find('.error').length) return false;
            
            data.more_info = _.escape(JSON.stringify({
                Screen  : window.screen.width + 'x' + window.screen.height,
                Window  : window.outerWidth   + 'x' + window.outerHeight,
                Browser : $.browser
            }));

            if (user) {
                data.user = user.get('nick') + ' (' + user.get('id') + ')';
            }

            $.ajax({
                url: '/feedback/',
                data: data,
                context: this,
                type: 'POST',
                success: function () { 
                    form.html(success_html);
                    setTimeout(function () {
                        $control.click();
                    }, 2000);
                },
                error: function () {
                    form.html(error_html);
                    setTimeout(function () {
                        $control.click();
                    }, 2000);
                }
            });
        }
    }
});

Backbone.Form.validators.errMessages = {
    required: 'Обязательное поле',
    regexp: 'Некорректное значение',
    email: 'Некорректный e-mail адрес',
    url: 'Некорректный url',
    youtube: 'Введите ссылку на видео с YouTube',
    positive_int: 'Введите положительное число'
};

Backbone.Form.validators.youtube = function(options) {
    options = _.extend({
      type: 'youtube',
      message: this.errMessages.youtube,
      regexp: /^(http|https):\/\/(www\.youtube\.com|youtu.be)\/[a-zA-Z0-9\?&\/=\-]+$/gmi
    }, options);
    
    return Backbone.Form.validators.regexp(options);
};

Backbone.Form.validators.positive_int = function(options) {
    options = _.extend({
      type: 'positive_int',
      message: this.errMessages.positive_int
    }, options);
     
    return function positive_int(value) {
      options.value = value;
      
      var err = {
        type: options.type,
        message: options.message
      };
      
      if (value === null || value === undefined || value === false || value === '' || value <= 0) return err;
    };
};

// Всякие штуки для форм
(function (Form){
    _.extend(Form.validators.errMessages, {
        required   : 'Обязательное поле',
        regexp     : 'Неверное значение',
        email      : 'Некорректный email',
        url        : 'Некорректный URL',
        match      : 'Значение должно быть вида "{{field}}"'
    });
   
    _.extend(Form.Field.prototype, {
        template:  _.template('\
            <div>\
              <label for="<%= editorId %>"><%= title %><span class="right"><%= help %></span></label>\
                <span data-editor></span>\
                <div data-error></div>\
            </div>\
          ', null, Form.templateSettings),

        setError: function (msg) {
            //Nested form editors (e.g. Object) set their errors internally
            if (this.editor.hasNestedForm) return;

            var label = this.$el.find('label'),
                title = label.text();

            if (title.indexOf('(') !== -1) return;

            label.addClass(this.errorClassName).text(title + ' (' + msg + ')');
            this.$el.find('input').addClass(this.errorClassName);
        },

        clearError: function() {
            var label = this.$el.find('label'),
                title = label.text().split('(')[0];

            label.text(title);

            //Remove error CSS class
            label.removeClass(this.errorClassName);
            this.$el.find('input').removeClass(this.errorClassName);
        }
    });

     _.extend(Form, {
        template: _.template('<form data-fieldsets class="vertical"></form>', null, Form.templateSettings)
    });

}(Backbone.Form));

