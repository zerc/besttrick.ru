/*
 * Views for tricks module
 */
 Besttrick.module('Tricks.Views', function (Views, App, Backbone, Marionette, $, _) {
    Views.CheckinForm = Backbone.Form.extend({
        className: 'trick__dialog',

        events: {
            'click a.dialog__close i': 'close',
            'click a.dialog__save': 'save'
        },

        render: function (args) {
            Backbone.Form.prototype.render.call(this, args);
            this.trigger('after:render');
   
            this.$el.find('input')
                .tooltip({trigger: 'focus'})
                .errortip({trigger: 'manual'});

            return this;
        },

        initialize: function (args) {
            Backbone.Form.prototype.initialize.call(this, args);
            
            this.model.on('change', function () {
                this.model.save();
                this.render()
            }, this);

            this.on('after:render', function () {
                console.log(this.$el);
                var w = args.parent.width(),
                    h = args.parent.height();
                this.$el.width(w+2).height(h-21);
            }, this);
        },

        save: function () {
            var self = this,
                errors = this.commit();

            if (!errors) { return false; }

            _.each(errors, function (k, v) {
                self.fields[v].editor.$el.addClass('error')
                    .tooltip('disable').errortip('enable').errortip('show')
                    .one('blur, keydown', function () {
                        $(this).errortip('hide').errortip('disable').tooltip('enable');
                    });
            });

            return false;
        },

        close: function () {
            $('div.tooltip').remove();
            this.remove();
            return false;
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
            var tmp = new Views.CheckinForm({
                model: model, 
                parent: this.$el,
                template: _.template($('#checkin_form').html())
            }).render();

            this.$el.append(
                tmp.el
            )
            return false;
        }
    });

    Views.Tricks = Backbone.Marionette.CollectionView.extend({
        tagName: 'div',
        className: 'tricks grid',
        itemView: Views.Trick,

        appendHtml: function (collectionView, itemView) {
            this.$el.append(itemView.el);
        }
    })
 });
