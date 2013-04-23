/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * Модели, вьюхи и вспомогательные функции, относящиеся к ачичкам
 */
window.BTAchives = {
    max_achive_lvl  : 3,
    common_phrases  : [
        '<br>Для того, чтобы получить достижение <a href="#" class="more_link">откатайте</a>:',
        '<br>Для получения следующего уровня достижения вам нужно <a href="#" class="more_link">откатать</a>:'
    ],
    cls_for_lvl: 'achive__lvl_'
};

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

    get_title: function () {
        return this.get('title') + ' lvl ' + this.get('level');
    },

    get_next_lvl: function () {
        return _.min([this.get('level')+1, window.BTAchives.max_achive_lvl]);
    },

    get_descr: function () {
        return this.get('descr') + window.BTAchives.common_phrases[_.min([this.get('level'), 1])];
    },

    get_time_changed: function () {
        var t = new Date(this.get('time_changed'));
        return t.format();
    },

    url: function () {
        var common_string = '/achives/achive' + this.get('id') + '/level' + this.get_level() + '/';

        if (this.get('user_id') === this.user.get('id')) {
            return '/my' + common_string;
        }

        return '/profile' + this.get('user_id') + common_string;
    },

    get_max_progress_for_lvl: function (for_lvl) {
        if (this.get('rule').cones) {
            return this.get('rule').cones[(for_lvl || this.get('level'))-1 || 0];
        }

        if (this.get('rule').complex) {
            return this.get('rule').complex;
        }
    },

    show_progress: function (for_lvl) {
        if (this.get('rule').cones) {
            var max = this.get_max_progress_for_lvl(for_lvl),
                formatted = max ? '/' + max : '',
                progress = this.get('progress')[0] || 0;                
            return _.template('<%= progress %><%= max %>', {progress: progress, max: formatted})
        }
    }
});


window.BTAchives.AchiveList = Backbone.Collection.extend({
    model: window.BTAchives.Achive,

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
window.BTAchives.AchiveView = Backbone.View.extend({
    tagName     : 'div',
    className   : 'achive',
    template    : new EJS({url: '/static/templates/achive.ejs'}),
    
    _cached     : false,

    events: {
        'click div.achive__header' : 'toggle',
        'click div.achive__text a.more_link' : 'toggle'
    },

    initialize: function (args) {
        _.bindAll(this, 'render', 'toggle');
        this.$el.addClass(window.BTAchives.cls_for_lvl + this.model.get('level'));
    },

    toggle: function () {
        // TODO: переписать так, чтобы от родителя можно было добраться до детей (поле childrens) =()
        var self = this,
            toggle_cls = 'showing_progress',
            childrens;

        if (this.$el.hasClass(toggle_cls)) {
            this.$el.removeClass(toggle_cls);
            return false;
        } else if (!this._cached) {
            childrens= this.model.collection.filter(function (e) {
                return _.include(e.get('parents'), self.model.id);
            });

            this.render({childrens: childrens});
            this._cached = true;
        }

        this.$el.addClass(toggle_cls);
        return false;
    },

    render: function (args) {
        var opts = {achive: this.model, childrens: []}
        _.extend(opts, args)
        this.$el.html(this.template.render(opts));
        this.$el.find('ul.achive__progress span, div.achive__status').tooltip();

        return this.$el;
    }
});


window.BTAchives.AchivesView = Backbone.View.extend({
    el: 'div.content',
    template: new EJS({url: '/static/templates/achives.ejs'}),

    initialize: function (args) {
        _.bindAll(this, 'render');
        this.collection = new window.BTAchives.AchiveList(args.base);
    },

    render: function (args) {
        var self = this,
            achives = [[], []],
            achive_list__cell,
            tmp;

        this.$el.html(this.template.render());        
        achive_list__cell = self.$el.find('.achive_list__cell');

        this.collection.fetch({success: function (a, b, c) {
            a.filter(function (e) { return e.get('rule').complex; })
             .forEach(function (e, i) {
                tmp = new window.BTAchives.AchiveView({model: e});
                $(achive_list__cell[i % 2]).append(tmp.render());
            });

            args.callback();
        }});
    }
});


