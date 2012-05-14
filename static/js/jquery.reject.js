/*
 * jReject (jQuery Browser Rejection Plugin)
 * Version 1.0.0
 * URL: http://jreject.turnwheel.com/
 * Description: jReject is a easy method of rejecting specific browsers on your site
 * Author: Steven Bower (TurnWheel Designs) http://turnwheel.com/
 * Copyright: Copyright (c) 2009-2011 Steven Bower under dual MIT/GPL license.
 */

(function($) {
$.reject = function(opts) {
	var opts = $.extend(true,{
		reject : { // Rejection flags for specific browsers
			all: false, // Covers Everything (Nothing blocked)
			msie5: true, msie6: true // Covers MSIE 5-6 (Blocked by default)
			/*
			 * Possibilities are endless...
			 *
			 * // MSIE Flags (Global, 5-8)
			 * msie, msie5, msie6, msie7, msie8,
			 * // Firefox Flags (Global, 1-3)
			 * firefox, firefox1, firefox2, firefox3,
			 * // Konqueror Flags (Global, 1-3)
			 * konqueror, konqueror1, konqueror2, konqueror3,
			 * // Chrome Flags (Global, 1-4)
			 * chrome, chrome1, chrome2, chrome3, chrome4,
			 * // Safari Flags (Global, 1-4)
			 * safari, safari2, safari3, safari4,
			 * // Opera Flags (Global, 7-10)
			 * opera, opera7, opera8, opera9, opera10,
			 * // Rendering Engines (Gecko, Webkit, Trident, KHTML, Presto)
			 * gecko, webkit, trident, khtml, presto,
			 * // Operating Systems (Win, Mac, Linux, Solaris, iPhone)
			 * win, mac, linux, solaris, iphone,
			 * unknown // Unknown covers everything else
			 */
		},
		display: [], // What browsers to display and their order (default set below)
		browserInfo: { // Settings for which browsers to display
			firefox: {
				text: 'Firefox 12', // Text below the icon
				url: 'http://www.mozilla.com/firefox/' // URL For icon/text link
			},
			safari: {
				text: 'Safari 5',
				url: 'http://www.apple.com/safari/download/'
			},
			opera: {
				text: 'Opera 11',
				url: 'http://www.opera.com/download/'
			},
			chrome: {
				text: 'Chrome 18',
				url: 'http://www.google.com/chrome/'
			},
			msie: {
				text: 'Internet Explorer 9',
				url: 'http://www.microsoft.com/windows/Internet-explorer/'
			},
			gcf: {
				text: 'Google Chrome Frame',
				url: 'http://code.google.com/chrome/chromeframe/',
				// This browser option will only be displayed for MSIE
				allow: { all: false, msie: true }
			}
		},

		paragraph: 'Just click on the icons to get to the download page'
	},opts);

	// Set default browsers to display if not already defined
	if (opts.display.length < 1)
		opts.display = ['firefox','chrome','msie','safari','opera','gcf'];

	// beforeRject: Customized Function
	if ($.isFunction(opts.beforeReject)) opts.beforeReject(opts);

	// Disable 'closeESC' if closing is disabled (mutually exclusive)
	if (!opts.close) opts.closeESC = false;

	// This function parses the advanced browser options
	var browserCheck = function(settings) {
		// Check 1: Look for 'all' forced setting
		// Check 2: Operating System (eg. 'win','mac','linux','solaris','iphone')
		// Check 3: Rendering engine (eg. 'webkit', 'gecko', 'trident')
		// Check 4: Browser name (eg. 'firefox','msie','chrome')
		// Check 5: Browser+major version (eg. 'firefox3','msie7','chrome4')
		return (settings['all'] ? true : false) ||
			(settings[$.os.name] ? true : false) ||
			(settings[$.layout.name] ? true : false) ||
			(settings[$.browser.name] ? true : false) ||
			(settings[$.browser.className] ? true : false);
	};

	// Determine if we need to display rejection for this browser, or exit
	if (!browserCheck(opts.reject)) {
		// onFail: Customized Function
		if ($.isFunction(opts.onFail)) opts.onFail(opts);
		return false;
	}

	// LMain wrapper (jr_wrap) +
	// Inner Wrapper (jr_inner)
	var html = '<div id="jr_inner"><p>'+opts.paragraph+'</p><ul>';

	var displayNum = 0; // Tracks number of browsers being displayed
	// Generate the browsers to display
	for (var x in opts.display) {
		var browser = opts.display[x]; // Current Browser
		var info = opts.browserInfo[browser] || false; // Browser Information

		// If no info exists for this browser
		// or if this browser is not suppose to display to this user
		if (!info || (info['allow'] != undefined && !browserCheck(info['allow']))) {
			continue;
		}

		var url = info.url || '#'; // URL to link text/icon to
		// Generate HTML for this browser option
		html += '<li id="jr_'+browser+'"><div class="jr_icon"></div>'+
				'<div><a target="_blank" href="'+url+'">'+(info.text || 'Unknown')+'</a>'+
				'</div></li>';
		++displayNum; // Increment number of browser being displayed
	}

	// Close list and #jr_list
	html += '</ul><div class="clear"></div></div>';

	var element = $(html); // Create element

	// Called onClick for browser links (and icons)
	// Opens link in new window
	var openBrowserLinks = function(url) {
		// Send link to analytics if enabled
		analytics(url);

		// Open window, generate random id value
		window.open(url, 'jr_'+ Math.round(Math.random()*11));

		return false;
	};

	// element.find('#jr_inner li').css({ // Browser list items (li)
	// 	background: 'transparent url("'+opts.imagePath+'background_browser.gif")'+
	// 				'no-repeat scroll left top'
	// });

	element.find('#jr_inner li .jr_icon').each(function() {
		// Dynamically sets the icon background image
		var self = $(this);
		// self.css('background','transparent url('+opts.imagePath+'browser_'+
		// 		(self.parent('li').attr('id').replace(/jr_/,''))+'.gif)'+
		// 			' no-repeat scroll left top');

		// Send link clicks to openBrowserLinks
		self.click(function () {
			var url = $(this).next('div').children('a').attr('href');
			openBrowserLinks(url);
		});
	});

	element.find('#jr_inner li a').click(function() {
		openBrowserLinks($(this).attr('href'));
		return false;
	});

	// Append element to body of document to display
	$('#jr_wrap').html(element).addClass('wrap_active');

	// afterReject: Customized Function
	if ($.isFunction(opts.afterReject)) opts.afterReject(opts);

	return true;
};
})(jQuery);

/*
 * jQuery Browser Plugin
 * Version 2.4 / jReject 1.0.0
 * URL: http://jquery.thewikies.com/browser
 * Description: jQuery Browser Plugin extends browser detection capabilities and
 * can assign browser selectors to CSS classes.
 * Author: Nate Cavanaugh, Minhchau Dang, Jonathan Neal, & Gregory Waxman
 * Updated By: Steven Bower for use with jReject plugin
 * Copyright: Copyright (c) 2008 Jonathan Neal under dual MIT/GPL license.
 */

(function ($) {
	$.browserTest = function (a, z) {
		var u = 'unknown',
			x = 'X',
			m = function (r, h) {
				for (var i = 0; i < h.length; i = i + 1) {
					r = r.replace(h[i][0], h[i][1]);
				}

				return r;
			}, c = function (i, a, b, c) {
				var r = {
					name: m((a.exec(i) || [u, u])[1], b)
				};

				r[r.name] = true;

				if (!r.opera) {
					r.version = (c.exec(i) || [x, x, x, x])[3];
				}
				else {
					r.version = window.opera.version();
				}

				if (/safari/.test(r.name) && r.version > 400) {
					r.version = '2.0';
				}
				else if (r.name === 'presto') {
					r.version = ($.browser.version > 9.27) ? 'futhark' : 'linear_b';
				}

				r.versionNumber = parseFloat(r.version, 10) || 0;
				var minorStart = 1;
				if (r.versionNumber < 100 && r.versionNumber > 9) {
					minorStart = 2;
				}
				r.versionX = (r.version !== x) ? r.version.substr(0, minorStart) : x;
				r.className = r.name + r.versionX;

				return r;
			};

		a = (/Opera|Navigator|Minefield|KHTML|Chrome/.test(a) ? m(a, [
			[/(Firefox|MSIE|KHTML,\slike\sGecko|Konqueror)/, ''],
			['Chrome Safari', 'Chrome'],
			['KHTML', 'Konqueror'],
			['Minefield', 'Firefox'],
			['Navigator', 'Netscape']
		]) : a).toLowerCase();

		$.browser = $.extend((!z) ? $.browser : {}, c(a,
			/(camino|chrome|firefox|netscape|konqueror|lynx|msie|opera|safari)/, [],
			/(camino|chrome|firefox|netscape|netscape6|opera|version|konqueror|lynx|msie|safari)(\/|\s)([a-z0-9\.\+]*?)(\;|dev|rel|\s|$)/
			)
		);

		$.layout = c(a, /(gecko|konqueror|msie|opera|webkit)/, [
			['konqueror', 'khtml'],
			['msie', 'trident'],
			['opera', 'presto']
		], /(applewebkit|rv|konqueror|msie)(\:|\/|\s)([a-z0-9\.]*?)(\;|\)|\s)/);

		$.os = {
			name: (/(win|mac|linux|sunos|solaris|iphone)/.
					exec(navigator.platform.toLowerCase()) || [u])[0]
						.replace('sunos', 'solaris')
		};

		if (!z) {
			$('html').addClass([$.os.name, $.browser.name, $.browser.className,
				$.layout.name, $.layout.className].join(' '));
		}
	};

	$.browserTest(navigator.userAgent);
}(jQuery));
