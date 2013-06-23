/*
 * Views for tricks module
 */
 Besttrick.module('Tricks.Views', function (Views, App, Backbone, Marionette, $, _) {
    Views.TricksFilter = Marionette.ItemView.extend({
        template: '#tricks_filter',
        className: 'button-bar tricks_filter',
        tagName: 'ul',

        events: {
            'click li': 'update_filter'
        },


        initialize: function (options) {
            this.templateHelpers = options.templateHelpers;
            this.listenTo(this, 'render', this.set_filter);
        },

        set_filter: function () {
            var tags_ids = location.hash.match(/^#filter=(.*)/);
                selector = '';

            if (!tags_ids) return;

            selector = _.map(tags_ids.pop().split(','), function (ti) {
                return 'a[href="#' + ti + '"]';
            }).join(',');
            this.$el.find(selector).addClass('inset');
        },

        update_filter: function (e) {
            $(e.target).toggleClass('inset');
            
            var selected_tags = _.map(this.$el.find('.inset'), function (e) {
                return $(e).attr('href').replace('#', '');
            });

            App.router.navigate(selected_tags.length > 0 ?
                'filter=' + selected_tags.join(',') : '', {trigger: true}
            );

            return false;
        }
    });    


    Views.TrickPage = Marionette.ItemView.extend({
        template: '#trick_page',
        className: 'grid trick_page',
        templateHelpers: App.Common.Functions,

        initialize : function () {
            this.listenTo(this.model, 'change', this.render);
            this.listenTo(this.model, 'checkins:loaded', this.render_checkins);

            this.listenTo(this, 'item:rendered', function () {
                this.model.get_checkins();
            });
        },

        render_checkins: function () {
            var container = this.$el.find('.trick__users');
            container.html(
                new Views.Checkins({
                    collection: this.model.get('checkins')
                }).render().el
            );
        }
    });

    Views.Trick = Marionette.ItemView.extend({
        template: '#trick_item',
        className: 'col_4 trick',
        
        templateHelpers: App.Common.Functions,

        events: {
            'click a.trick__check i': 'render_form'
        },

        initialize : function () {
            this.listenTo(this.model, 'change', this.render);
        },

        render_form: function () {
            var model = this.model.get('user_checkin') || new App.Tricks.Models.Checkin()
            model.trick_id = this.model.get('id');
            // model.set('trick', this.model, {silent: true});

            var tmp = new Views.CheckinForm({
                model: model, 
                parent: this,
                template: _.template($('#checkin_form').html())
            }).render();

            this.$el.append(tmp.el);
            return false;
        }
    });

    Views.Tricks = Backbone.Marionette.CollectionView.extend({
        tagName: 'div',
        className: 'tricks grid',
        itemView: Views.Trick,
        filter_tricks_ids: [],

        initialize : function () {
            this.listenTo(this, 'filterd', this.render, this);
        },

        set_filter: function (filter_tricks_ids, trigger) {
            this.filter_tricks_ids = filter_tricks_ids || [];
            if (trigger) this.trigger('filterd');
        },

         // TODO: mb rewrite table>tr>td to div?
        appendHtml: function (collectionView, itemView, index) {
            if (this.filter_tricks_ids.length > 0 && !_.contains(this.filter_tricks_ids, itemView.model.id)) {
                return;
            }
            Backbone.Marionette.CollectionView.prototype.appendHtml.call(this, collectionView, itemView, index);
        }

    })
 });
