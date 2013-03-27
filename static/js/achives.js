/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * Модели, вьюхи и вспомогательные функции, относящиеся к ачичкам
 */
window.BTAchives = {};

/* Models */
window.BTAchives.Achive = Backbone.Model.extend({
    // Ачивка. Если указан пользователь - то отмечается его прогресс по ачивке
    defaults: {
        title           : '',
        descr           : '',
        icon            : '',
        score           : 0.0,
        trick_id        : null,                        
        rule            : {},
        parents         : [],

        progress        : [],
        done            : false,        
        user_id         : null,
        time_changed    : '',
        level           : 0
    },

    initialize: function (user) {
        var self = this;
        this.user = user
    },

    get_rule_name: function () {
        return _.keys(this.get('rule'))[0];
    },

    get_level: function () {
        return this.get('level');
    },

    url: function () {
        var common_string = '/achives/achive' + this.get('id') + '/level' + this.get_level() + '/';

        if (this.get('user_id') === this.user.get('id')) {
            return '/my' + common_string;
        }

        return '/profile' + this.get('user_id') + common_string;
    },

    get_max_progress_for_lvl: function () {
        if (this.get('rule').cones) {
            return this.get('rule').cones[this.get_level()];
        }

        if (this.get('rule').complex) {
            return this.get('rule').complex;
        }
    },

    get_descr: function () {
        var text_tmpl = this.get('descr') + '<br>',
            progress = this.get_max_progress_for_lvl();

        if (this.get('rule').cones) {
            if (progress) {
                return _.template(text_tmpl, {
                    'cones': EJS.Helpers.prototype.plural(progress,
                    'банка', 'банки', 'банок')
                }); 
            } else {
                return 'Нет предела совершенству, но вы на правильном пути!<br>';
            }
        }

        return this.get('descr');
    },

    show_progress: function () {
        if (this.get('rule').cones) {
            var max = this.get_max_progress_for_lvl(),
                formatted = max ? '/ ' + max : '',
                progress = this.get('progress')[0] || 0;
            return _.template('Выполнено <%= progress %> <%= max %>', {progress: progress, max: formatted})
        }

        if (this.get('rule').complex) {
            window.at = this.collection
            var tmpl = "Чтобы получить следующий уровень достижения нужно:<br><%= els %>",
                max_lvl = _.max(this.collection.map(function (e) { return e.get('level'); })) || 1,
                e,
                els = _.map(this.get('rule').complex, function (e, i) {
                    e = this.collection.get(e);
                    return '<span' + (e.get('level') == max_lvl ? ' class="done">' : '>') + e.get('title') + ' (' + e.get('level') + ')</span>';
                }, this);

            return _.template(tmpl, {
                els: els.join(' ')
            });
        }
    }
});


window.BTAchives.AchiveList = Backbone.Collection.extend({
    model: window.BTAchives.Achive,

    level: 1,

    url: function () {
        return this.base + '/achives/';
    },

    initialize: function (base) {
        this.base = base || '/my';
    },

    parse: function(resp, xhr) {
      return resp.achives;
    }
});


/*** Views ***/
window.BTAchives.AchivesView = Backbone.View.extend({
    el: 'div.content',
    template: new EJS({url: '/static/templates/achives.ejs'}),

    events: {
        'click a.achives_level': 'change_level'
    },

    initialize: function (args) {
        _.bindAll(this, 'render');
        this.collection = new window.BTAchives.AchiveList(args.base);
    },

    change_level: function () {

    },

    render: function (args) {
        var self = this;

        this.collection.level = args.level;
        this.collection.fetch({success: function (a, b, c) {
            self.$el.html(self.template.render({achives: a}));
            args.callback();
        }})
    }
});


