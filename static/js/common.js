/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * Файл содержит общие для всего приложения элементы.
 */
window.BTCommon = _.extend({
    vars: {
        // кука в которую сохраняется url страницы с которой логинились 
        // (туда будет выполнен редирект после логина)
        next_url_cookie_name: 'next',

        // имя куки для сохранения данных чекина навторизованного пользователя
        tmp_trick_cookie_name: 'trick'
    },

    ajax: function (context, opts) {
        var self = this;
        opts.success = _.wrap(opts.success, function (f, response) {
            var result = f(response);
            self.trigger('ajax_done');
            return result;
        });
        return $.ajax(opts);
    },

    get_youtube_video_id: function (video_url) {
        if (/embed|youtu\.be/.test(video_url)) return video_url.split('/').pop();
        if (/\/watch\?v=/.test(video_url)) return /\?v=([^&]+)/.exec(video_url).pop();
        if (/img.youtube.com/.test(video_url)) return /vi\/([^&]+)\//.exec(video_url).pop();
        throw "Can't parse video_url string!";
    }
}, Backbone.Events);


if (typeof String.prototype.trim !== 'function') {
    String.prototype.trim = function() {
        return this.replace(/^\s+|\s+$/g, ''); 
    }
};

/*** EJS ***/

/* Eсли в имени пользователя больше двух слов - первое выводим полностью, а второе сокращаем */
EJS.Helpers.prototype.format_username = function (username) {
    var parts = username.trim().split(' ');
    return parts[1] ? parts[0] + ' ' + parts[1].charAt(0).toUpperCase() + '.' : parts[0];
};


/* Выводит пару key:value если value не null */
EJS.Helpers.prototype.print_value_if_exists = function (key, value) {
    if (value) return '<p><strong>' + key + ':</strong> ' + value + '</p>';
};


EJS.Helpers.prototype.set_page_title = function (title) {
    window.document.title = 'Besttrick - ' + title;
};


EJS.Helpers.prototype.plural = function(number, one, two, five) {
    var n = Math.abs(number);

    n %= 100;
    if (n >= 5 && n <= 20) return number + ' ' + five;

    n %= 10;
    if (n == 1) return number + ' ' + one;

    if (n >= 2 && n <= 4) return number + ' ' + two;

    return number + ' ' + five;
};


EJS.Helpers.prototype.browser_info = function () {
    var data = {
        Screen  : window.screen.width + 'x' + window.screen.height,
        Window  : window.outerWidth   + 'x' + window.outerHeight,
        Browser : $.browser
    }
    return _.escape(JSON.stringify(data));
};

EJS.Helpers.prototype.render_video_thumb = function (video_url, title) {
    var thumb_url = window.BTCommon.get_youtube_video_id(video_url);
    return '<img src="http://img.youtube.com/vi/'+thumb_url+'/1.jpg" alt="'+title+'" height="50" />';
};

// Переопределим кое-что в date.format плагине
dateFormat.masks["default"] = "dd mmmm yyyy HH:MM";

dateFormat.i18n = {
    dayNames: [
        "Воскр", "Пон", "Вт", "Ср", "Чет", "Пят", "Суб",
        "Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"
    ],
    monthNames: [
        "Янв", "Фев", "Мар", "Апр", "Мая", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек",
        "Января", "Февраля", "Марта", "Апреля", "Мая", "Июня", "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"
    ]
};


// Всякие штуки для форм
(function (){
    _.extend(Backbone.Form.validators.errMessages, {
        required   : 'Обязательное поле',
        regexp     : 'Неверное значение',
        email      : 'Некорректный email',
        url        : 'Некорректный URL',
        match      : 'Значение должно быть вида "{{field}}"'
    });

    Backbone.Form.setTemplates({
        form: '\
          <form class="bbf-form">{{fieldsets}}</form>\
        ',
        
        fieldset: '\
          <fieldset>\
            {{legend}}\
            {{fields}}\
          </fieldset>\
        ',
        
        field: '\
        <span>\
          <div class="bbf-editor bbf-editor{{type}}">{{editor}}</div>\
          <div class="bbf-help">{{help}}</div>\
        </span>\
        '
    });
}());
