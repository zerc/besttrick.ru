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

    url: function () {
        var common_string = '/achives/achive' + this.get('id') + '/level' + this.get('level') + '/';

        if (this.get('user_id') === this.user.get('id')) {
            return '/my' + common_string;
        }

        return '/profile' + this.get('user_id') + common_string;
    },

    get_max_progress_for_lvl: function () {
        if (this.get('rule').cones) {
            return this.get('rule').cones[this.get('level') - 1];
        }

        if (this.get('rule').complex) {
            return this.get('rule').complex;
        }
    },

    get_descr: function () {
        var text_tmpl = this.get('descr') + '<br>';

        if (this.get('rule').cones) {
            return _.template(text_tmpl, {
                'cones': EJS.Helpers.prototype.plural(this.get_max_progress_for_lvl(),
                'банка', 'банки', 'банок')
            });
        }

        return this.get('descr');

    },

    show_progress: function () {
        if (this.get('rule').cones) {
            var max = this.get_max_progress_for_lvl(),
                max_index = this.get('rule').cones.indexOf(max),
                min = this.get('rule').cones[_.max([0, max_index-1])];
            min = _.max([min, this.get('progress')[0]]);
            return _.template('Выполнено <%= min %> / <%= max %>', {min: min, max: max})
        }

        if (this.get('rule').complex) {
            var tmpl = "Чтобы получить достижение нужно выполнить следующее:<br><%= els %>",
                els = _.map(this.get('rule').complex, function (e, i) {
                    var el = this.collection.get(e);
                    el.done = _.include(this.get('progress'), el.id);
                    return el;
                }, this);

            els = _.map(els, function (e, i) {
                return '<span' + (e.done ? ' class="done">' : '>') + e.get('title') + '</span>';
            });

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
        return this.base + '/achives/?level=' + this.level;
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


