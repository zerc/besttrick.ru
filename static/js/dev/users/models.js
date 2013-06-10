/*global Besttrick */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * Models for users module
 */

Besttrick.module('Users.Models', function (Models, App, Backbone, Marionette, $, _) {
    Models.User = App.Common.Model.extend({
        url: '/user/',

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
                type        : 'Text', 
                validators  : ['required'],
                editorAttrs : {'placeholder': 'Ник', 'maxlength': '100'}
            },
            team: {
                type: 'Text', 
                editorAttrs : {'placeholder': 'Команда', 'maxlength': '100'}
            },
            phone: {
                type: 'Text',
                editorAttrs : {'placeholder': 'Телефон'}
            },
            city: {
                type: 'Text', 
                editorAttrs : {'placeholder': 'Город', 'maxlength': '100'}
            },
            icq: {
                type: 'Text', 
                editorAttrs : {'placeholder': 'ICQ', 'maxlength': '10'}
            },
            skype: {
                type: 'Text', 
                editorAttrs: {'placeholder': 'Skype', 'maxlength': '50'}
            },
            rolls: {
                type: 'Text',
                editorAttrs: {'placeholder': 'Ролики', 'maxlength': '50'}
            },
            epxs: {
                type: 'Text',
                editorAttrs: {'placeholder': 'Стаж', 'maxlength': '50'}
            },
            bio: {
                type: 'TextArea',
                editorAttrs: {'placeholder': 'Информация', 'maxlength': '300'}
            }
        },

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

        validate: function (attrs) {
            if (!attrs.nick) {
                return 'укажите свой ник';
            }

            if (attrs.nick.length >= 125) {
                return 'у вас нереально большой ник';
            }
        },

        get_profile_url: function () {
            return '#!users/user' + this.id;
        },

        parse: function(resp, xhr) {
          return resp.user;
        }
    });
});
