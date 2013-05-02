/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * Файл содержит общие для всего приложения элементы
 */
window.BTCommon = {
    vars: {
        // кука в которую сохраняется url страницы с которой логинились 
        // (туда будет выполнен редирект после логина)
        next_url_cookie_name: 'next',

        // имя куки для сохранения данных чекина навторизованного пользователя
        tmp_trick_cookie_name: 'trick'
    },

    ajax: function (context, opts) {
        opts.success = _.wrap(opts.success, function (f, response) {
            var result = f(response);
            context.trigger('ajax_done');
            return result;
        });
        return $.ajax(opts);
    }
};


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
