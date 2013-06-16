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
            checkins    : []
        },

        wrappers: {
            'best_checkin': Models.Checkin,
            'user_checkin': Models.Checkin
        },

        props: ['get_thumb', 'get_title', 'get_href'],
        methods: ['large_img'],

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

        large_img: function (full) {
            var relative_path = '/static/images/trick' + this.id + '-0.jpg';

            return  full ? 'http://' + location.host + ':' + location.port + relative_path
                         : relative_path;
        },
        
        get_checkins: function () {
            var self = this,
                ch = new Models.Checkins();

            ch.fetch({
                data: 'fname=trick&id=' + this.id,
                success: function (checkins) {
                    self.set('checkins', checkins, {silent: true});
                    self.trigger('checkins:loaded');
                }
            });
        }
    });

    Models.Tricks = Backbone.Collection.extend({
        url: '/tricks/',
        model: Models.Trick,

        parse: function(resp, xhr) {
          return resp.tricks_list;
        },
    });

    Models.Checkins = Backbone.Collection.extend({
        url: '/checkins/',
        model: Models.Checkin,

        parse: function(resp, xhr) {
          return resp.checkins;
        }
    });


});
