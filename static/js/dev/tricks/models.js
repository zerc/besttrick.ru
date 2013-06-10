/*global Besttrick */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * Models for tricks module
 */

Besttrick.module('Tricks.Models', function (Models, App, Backbone, Marionette, $, _) {
    Models.Checkin = App.Common.Model.extend({
        url: '/checkin/',

        defaults: {
            cones: 0,
            approved: false,
            video_url: ''
        },

         wrappers: {
            'user': App.Users.Models.User
        },

        schema: {
            cones: {
                type        : 'Number', 
                validators  : ['required', 'positive_int'],
                editorAttrs : {
                    'placeholder': 'сколько банок?', 
                    'maxlength': '3', 
                    'title': 'На сколько конусов делаете трюк?',
                    'data-error-title': Backbone.Form.validators.errMessages.positive_int
                }
            },
            video_url: {
                type: 'Text',
                validators  : ['youtube'],
                editorAttrs : {
                    'placeholder': 'ссылка на видео', 
                    'maxlength': '200', 
                    'title': 'Ссылка на ваше видео с YouTube', 
                    'data-error-title': Backbone.Form.validators.errMessages.youtube
                },
            }
        }
    });

    Models.Trick = App.Common.Model.extend({
         defaults: {
            title       : '',
            thumb       : '',
            videos      : [],
            descr       : '',
            descr_html  : '',
            direction   : '',
            score       : 0,
            wssa_score  : 0,
            tags        : [],
        },

        wrappers: {
            'best_checkin': Models.Checkin,
            'user_checkin': Models.Checkin
        },

        methods: ['get_thumb', 'get_title', 'get_href'],

        get_thumb: function () {
            return '/static/images/' + this.get('thumb');
        },

        get_title: function () {
                return (this.get('title') + ' ' + (this.get('direction') || '')).trim();
        },

        get_href: function () {
            return '#!trick' + this.get('id');
        },

        url: function () {
            return '/tricks/trick' + this.get('id')
        },

        toJSON: function() {
            var attrs = Backbone.Model.prototype.toJSON.call(this);
            this.extend_methods(attrs)
            console.log(attrs);
            return attrs;
        }
    });

    Models.Tricks = Backbone.Collection.extend({
        url: '/tricks/',
        model: Models.Trick,

        parse: function(resp, xhr) {
          return resp.tricks_list;
        },
    });
});
