/*global Besttrick */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * Models for achives module
 */

Besttrick.module('Achives.Models', function (Models, App, Backbone, Marionette, $, _) {
    Models.Achive = App.Common.Model.extend({
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

        props: ['get_rule_name', 'get_title', 'get_next_lvl', 'get_descr', 'get_time_changed', 'get_childrens'],
        methods: ['get_max_progress_for_lvl', 'show_progress', 'get_childrens'],

        is_complex: function () {
            return !!this.get('rule').complex;
        },

        initialize: function (user, tricks) {
            this.user_id = this.collection.user_id;
            this.tricks = this.collection.tricks;
        },

        get_trick: function () {
            // TODO: make this better
            return this.tricks.get({'id': this.get('trick_id')});
        },

        get_rule_name: function () {
            return _.keys(this.get('rule'))[0];
        },

        get_title: function () {
            return (this.is_complex() ? this.get('title') : this.get_trick().get_title()) 
                    + ' lvl ' + this.get('level');
        },

        get_next_lvl: function () {
            return _.min([this.get('level')+1, App.Achives.max_achive_lvl]);
        },

        get_descr: function () {
            return this.get('descr') + App.Achives.common_phrases[_.min([this.get('level'), 1])];
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

            if (this.get('user_id') === this.user_id) {
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

    Models.AchiveList = Backbone.Collection.extend({
        model: Models.Achive,

        show_level: -1,

        url: function () {
            return _.isUndefined(this.user_id) ?
                    '/my/achives/' : '/users/user' + this.user_id + '/achives/';
        },

        initialize: function (opts) {
            this.user_id = opts.user_id;
            this.tricks = opts.tricks;
        },

        parse: function(resp, xhr) {
          return resp.achives;
        }
    });
});
