/*
 * Views for tricks module
 */
Besttrick.module('Users.Views', function (Views, App, Backbone, Marionette, $, _) {
    var BaseBarView = Marionette.ItemView.extend({
        template: '#user_login_bar',
        className: 'user_container pull-right',
        events: {
            'click a.loginza': 'save_path',
            'click a.logout' : 'save_path'
        },

        save_path: function (e) {
            var path = location.hash;
            if (!path) return;
            $.cookie(App.Common.Vars.next_url_cookie_name, encodeURIComponent(path));
        }
    });
        
    Views.LoginBar = BaseBarView.extend({
        templateHelpers: {
            Loginza: {
                href: "https://loginza.ru/api/widget?token_url=http://"
                    + location.host 
                    + "/login/&providers_set=vkontakte,twitter,facebook",

                // Просто обертка метода библиотеки
                show_login_form: function () {
                    if (!LOGINZA || !LOGINZA.show) {
                        return alert('Cant find LOGINZA widget :/');
                    }

                    LOGINZA.show.call(this);
                }
            }
        }
    });

    Views.UserBar = BaseBarView.extend({
        className: 'user_container pull-right',
        template: '#user_bar',

        initialize: function () {
            this.listenTo(this.model, 'change', this.render);
        }
    });

    Views.User = Marionette.ItemView.extend({
        template : '#user_page',
        className: 'grid user_page',
        events   : {
            'click button.save': 'save'
        },

        // Dirty, very
        templateHelpers: {
            achives_url: '#!u/achives'
        },

        render_form: function () {
            this.form = new Backbone.Form({model: this.model}).render();
            this.$el.find('form').replaceWith(this.form.$el.append(
                $('<button>', {'type': 'button', 'class': 'save', 'text': 'Сохранить'})
            ));            
        },

        show_notice: function (text, type) {
            var el = $('<div class="notice ' + type + '">\
                '+ text +'<i class="icon-remove-sign icon-large"></i>\
                <a href="#close" class="icon-remove"></a></div>');
            this.$el.find('.notice').remove();
            this.$el.find('form').prepend(el);
        },

        render_checkins: function () {
            var container = this.$el.find('.trick__users');
            container.html(
                new Views.Checkins({
                    collection: this.model.get('checkins')
                }).render().el
            );
        },

        initialize: function () {
            var self = this;
            this.listenTo(this, 'render', this.render_form)
            this.listenTo(this.model, 'checkins:loaded', this.render_checkins);

            this.listenTo(this, 'render', function () {
                this.model.get_checkins();
            });           
        },

        save: function () {
            var self = this,
                errors = this.form.commit();

            if (errors) return self.show_notice('Ошибка', 'error');

            this.model.save(null, {
                success: function (model, response) { self.show_notice('Данные обновлены', 'success'); },
                error: function (model, response) { self.show_notice(response.statusText, 'error'); }
            });
        }
    });

    Views.UserProfile = Views.User.extend({
        templateHelpers: function () {
            return {
                achives_url: '#!users/user' + this.model.get('id') + '/achives'
            }
        },

        render_form: function () {
            this.form = new Backbone.Form({model: this.model}).render();            
            this.$el.find('form').replaceWith(this.form.$el);            
        }
    });
 });
