/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * Файл содержит общие для всего приложения элементы
 */
window.BTCommon = {};


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
