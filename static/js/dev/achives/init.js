Besttrick.module('Achives', function (Achives, App, Backbone, Marionette, $, _) {
    Achives.max_achive_lvl = 3,
    Achives.common_phrases = [
        // 0 lvl
        '<br>Для того, чтобы получить достижение <a href="#" class="more_link">откатайте</a>:',
        // 1+ lvl
        '<br>Для получения следующего уровня достижения вам нужно <a href="#" class="more_link">откатать</a>:'
    ],
    Achives.cls_for_lvl = 'achive__lvl_',

    Achives.url = function () {
        return '#!u/achives';
    },

    Achives.url_for_profile = function (user_id) {
        return '#!users/user' + user_id + '/achives';
    }
});
