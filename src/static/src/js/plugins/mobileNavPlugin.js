/* eslint-disable */

/*
 * Simple Mobile Navigation
 */
;((($) => {
	function MobileNav(options) {
		this.options = $.extend({
			container: null,
			hideOnClickOutside: false,
			menuActiveClass: 'nav-active',
			menuOpener: '.nav-opener',
			menuDrop: '.nav-drop',
			toggleEvent: 'click',
			outsideClickEvent: 'click touchstart pointerdown MSPointerDown'
		}, options);
		this.initStructure();
		this.attachEvents();
	}
	MobileNav.prototype = {
		initStructure: function() {
			this.page = $('html');
			this.container = $(this.options.container);
			this.opener = this.container.find(this.options.menuOpener);
      this.drop = this.container.find(this.options.menuDrop);
      this.makeCallback('onInit');
		},
		attachEvents: function() {

			if(activateResizeHandler) {
				activateResizeHandler();
				activateResizeHandler = null;
			}

			this.outsideClickHandler = (e) => {
				if(this.isOpened()) {
					const target = $(e.target);
					if(!target.closest(this.opener).length && !target.closest(this.drop).length) {
						this.hide();
					}
				}
			};

			this.openerClickHandler = (e) => {
				e.preventDefault();
				this.toggle();
			};

			this.opener.on(this.options.toggleEvent, this.openerClickHandler);
		},
		isOpened: function() {
			return this.container.hasClass(this.options.menuActiveClass);
		},
		show: function() {
      this.container.addClass(this.options.menuActiveClass);
			if(this.options.hideOnClickOutside) {
				this.page.on(this.options.outsideClickEvent, this.outsideClickHandler);
      }
      this.makeCallback('onShow');
		},
		hide: function() {
      this.container.removeClass(this.options.menuActiveClass);
      this.makeCallback('onHide');
			if(this.options.hideOnClickOutside) {
				this.page.off(this.options.outsideClickEvent, this.outsideClickHandler);
			}
		},
		toggle: function() {
			if(this.isOpened()) {
				this.hide();
			} else {
				this.show();
			}
		},
		destroy: function() {
			this.container.removeClass(this.options.menuActiveClass);
			this.opener.off(this.options.toggleEvent, this.clickHandler);
			this.page.off(this.options.outsideClickEvent, this.outsideClickHandler);
    },
    makeCallback (name) {
      if (typeof this.options[name] === 'function') {
        // biome-ignore lint/style/noArguments: <explanation>
        const args = Array.prototype.slice.call(arguments);
        args.shift();
        this.options[name].apply(this, args);
      }
    },
	};

	let activateResizeHandler = () => {
		const win = $(window);
		const doc = $('html');
		const resizeClass = 'resize-active';
		let flag;
		let timer;
		const removeClassHandler = () => {
			flag = false;
			doc.removeClass(resizeClass);
		};
		const resizeHandler = () => {
			if(!flag) {
				flag = true;
				doc.addClass(resizeClass);
			}
			clearTimeout(timer);
			timer = setTimeout(removeClassHandler, 500);
		};
		win.on('resize orientationchange', resizeHandler);
	};

	$.fn.mobileNav = function(opt) {
		// biome-ignore lint/style/noArguments: <explanation>
		const args = Array.prototype.slice.call(arguments);
		const method = args[0];

		return this.each(function() {
			const $container = jQuery(this);
			const instance = $container.data('MobileNav');

			if (typeof opt === 'object' || typeof opt === 'undefined') {
				$container.data('MobileNav', new MobileNav($.extend({
					container: this
				}, opt)));
			} else if (typeof method === 'string' && instance) {
				if (typeof instance[method] === 'function') {
					args.shift();
					instance[method].apply(instance, args);
				}
			}
		});
	};
})(jQuery));