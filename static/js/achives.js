/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * Модели, вьюхи и вспомогательные функции, относящиеся к ачичкам
 */
window.BTAchives = {
    max_achive_lvl  : 3,
    common_phrases  : [
    // 0 lvl
    '<br>Для того, чтобы получить достижение <a href="#" class="more_link">откатайте</a>:',
    // 1+ lvl
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

    is_complex: function () {
        return !!this.get('rule').complex;
    },

    initialize: function (user) {
        var self = this;
        this.user = user
    },

    get_trick: function () {
        return window.BTCommon.args.tricks.get({'id': this.get('trick_id')});
    },

    get_rule_name: function () {
        return _.keys(this.get('rule'))[0];
    },

    get_title: function () {
        return this.is_complex() ? this.get('title') : this.get_trick().get_title();
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

    get_childrens: function () {
        var children_ids = this.get('rule').complex || [];
        return _.map(children_ids, function (c_id) {return this.collection.get(c_id);}, this);        
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
        window.at = this.model.collection;
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
            this.render({childrens: this.model.get_childrens()});
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

    level_filter: false,

    events : {
        'click div.achives_filter a' : 'apply_filter'
    },

    initialize: function (args) {
        _.bindAll(this, 'render', 'apply_filter');
        this.collection = new window.BTAchives.AchiveList();
        this.collection.on('change', this.render);
    },

    reset_filter: function () {
        this.level_filter = false;
        return this;
    },

    apply_filter: function (e) {
        var $el = $(e.currentTarget),
            level = parseInt($el.attr('href').split(':')[1]);

        this.$el.find('div.achives_filter a').removeClass('active');

        if (this.level_filter === level) {
            this.level_filter = false;
            $el.removeClass('active');
        } else {
            this.level_filter = level;
            $el.addClass('active');
        }

        this.collection.trigger('change');
        return false;
    },

    filtered_collection: function () {
        var self = this;

        return this.collection.filter(function (e) {
            return e.get('rule').complex && (_.isNumber(self.level_filter) ? e.get('level') === self.level_filter : true);
        });
    },

    base_render: function () {        
        this.$el.html(this.template.render({view: this}));
        this.empty_list_el = this.$el.find('div.achive_list__empty');
        return this;
    },

    render: function (args) {
        var achive_list__cell = this.$el.find('.achive_list__cell'),
            collection = this.filtered_collection();

        achive_list__cell.html('');

        if (collection.length === 0) {
            this.empty_list_el.show();
        } else {
            this.empty_list_el.hide();
            collection.forEach(function (e, i) {
                $(achive_list__cell[i % 2]).append(new window.BTAchives.AchiveView({model: e}).render());
            });
        }
    }
});


