/*
 * Avoid cross imports for models
 */


_.extend(Besttrick.Tricks.Models.Checkin.prototype, {
    wrappers: {
        'user': Besttrick.Users.Models.User,
        'trick': Besttrick.Tricks.Models.Trick
    }
});
