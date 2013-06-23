/*global Besttrick */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * Models for users module
 */

Besttrick.module('Users.Models', function (Models, App, Backbone, Marionette, $, _) {
    Models.User = App.Common.Model.extend({
        url: function () {
            return '/users/user' + this.id + '/';
        },

        parse: function (response) {
            return response.user;
        },

        defaults: {
            uid      : '',
            nick     : '',
            team     : '',
            photo    : '',
            admin    : '',
            email    : '',
            city     : '',
            icq      : '',
            skype    : '',
            phone    : '',
            bio      : '',
            rolls    : '',
            epxs     : '',
            rating   : 0.0,
            banned   : false,

            selected_titul   : 0,
            titul: ''
        },

        schema: {
            nick: {
                title       : 'Ник',
                type        : 'Text', 
                validators  : ['required'],
                editorAttrs : {'placeholder': 'Ник', 'maxlength': '100'}
            },
            team: {
                title: 'Команда',
                type: 'Text', 
                editorAttrs : {'placeholder': 'Команда', 'maxlength': '100'}
            },
            phone: {
                title: 'Телефон',
                type: 'Text',
                editorAttrs : {'placeholder': 'Телефон'}
            },
            city: {
                title: 'Город',
                type: 'Text', 
                editorAttrs : {'placeholder': 'Город', 'maxlength': '100'}
            },
            icq: {
                title: 'ICQ',
                type: 'Text', 
                editorAttrs : {'placeholder': 'ICQ', 'maxlength': '10'}
            },
            skype: {
                title: 'Skype',
                type: 'Text', 
                editorAttrs: {'placeholder': 'Skype', 'maxlength': '50'}
            },
            rolls: {
                title: 'Ролики',
                type: 'Text',
                editorAttrs: {'placeholder': 'Ролики', 'maxlength': '50'}
            },
            epxs: {
                title: 'Стаж',
                type: 'Text',
                editorAttrs: {'placeholder': 'Стаж', 'maxlength': '50'}
            },
            bio: {
                title: 'Информация',
                type: 'TextArea',
                editorAttrs: {'placeholder': 'Информация'}
            }
        },

        props: ['get_profile_url', 'get_formatted_nick'],

        // initialize: function () {
        //     var self = this;

        //     this.schema.selected_titul = {
        //         type: 'SpecialSelect',
        //         editorAttrs: {'class': 'tituls_list'},
        //         options: function (callback) {
        //             var tituls = new TitulCollection().fetch({
        //                 'data': 'user_id=' + self.get('id'),
        //                 'success': function (response) {
        //                     callback(response);
        //                 }
        //             });
        //         }
        //     }

        //     this.schema = _.clone(this.schema);
        // },


        get_profile_url: function () {
            return '#!users/user' + this.id;
        },

        // parse: function(resp, xhr) {
        //   return resp.user;
        // },

        // TODO: make this better
        get_formatted_nick: function () {
            if (this.get('nick').length < 10) return this.get('nick');
            return this.get('nick').slice(0, 6) + '...';
        },

        get_checkins: function () {
            var self = this,
                ch = new App.Tricks.Models.Checkins();

            ch.fetch({
                data: 'fname=user&id=' + this.id,
                success: function (checkins, a, c) {
                    self.set('checkins', checkins, {silent: true});
                    self.trigger('checkins:loaded');
                }
            });
        }
    });

    Models.Users = Backbone.Collection.extend({
        url: '/users/',
        model: Models.User,

        parse: function(resp, xhr) {
          return resp.users;
        }
    });
});
