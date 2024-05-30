/* eslint-disable */

/*
 * Popups plugin
 */
;((($) => {
	function ContentPopup(opt) {
		this.options = $.extend({
			holder: null,
			popup: '.popup',
			btnOpen: '.open',
			btnClose: '.close',
			openClass: 'popup-active',
			clickEvent: 'click',
			mode: 'click',
			hideOnClickLink: true,
			hideOnClickOutside: true,
			delay: 50
		}, opt);
		if (this.options.holder) {
			this.holder = $(this.options.holder);
			this.init();
		}
	}
	ContentPopup.prototype = {
		init: function() {
			this.findElements();
			this.attachEvents();
		},
		findElements: function() {
			this.popup = this.holder.find(this.options.popup);
			this.btnOpen = this.holder.find(this.options.btnOpen);
			this.btnClose = this.holder.find(this.options.btnClose);
		},
		attachEvents: function() {
			this.clickMode = isTouchDevice || (this.options.mode === this.options.clickEvent);

			if (this.clickMode) {
				// handle click mode
				this.btnOpen.bind(`${this.options.clickEvent}.popup`, (e) => {
					if (this.holder.hasClass(this.options.openClass)) {
						if (this.options.hideOnClickLink) {
							this.hidePopup();
						}
					} else {
						this.showPopup();
					}
					e.preventDefault();
				});

				// prepare outside click handler
				this.outsideClickHandler = this.bind(this.outsideClickHandler, this);
			} else {
				// handle hover mode
				let timer;
				const delayedFunc = (func) => {
					clearTimeout(timer);
					timer = setTimeout(() => {
						func.call(this);
					}, this.options.delay);
				};
				this.btnOpen.on('mouseover.popup', () => {
					delayedFunc(this.showPopup);
				}).on('mouseout.popup', () => {
					delayedFunc(this.hidePopup);
				});
				this.popup.on('mouseover.popup', () => {
					delayedFunc(this.showPopup);
				}).on('mouseout.popup', () => {
					delayedFunc(this.hidePopup);
				});
			}

			// handle close buttons
			this.btnClose.on(`${this.options.clickEvent}.popup`, (e) => {
				this.hidePopup();
				e.preventDefault();
			});
		},
		outsideClickHandler: function(e) {
			// hide popup if clicked outside
			const targetNode = $((e.changedTouches ? e.changedTouches[0] : e).target);
			if (!targetNode.closest(this.popup).length && !targetNode.closest(this.btnOpen).length) {
				this.hidePopup();
			}
		},
		showPopup: function() {
			// reveal popup
			this.holder.addClass(this.options.openClass);
			this.popup.css({
				display: 'block'
			});

			// outside click handler
			if (this.clickMode && this.options.hideOnClickOutside && !this.outsideHandlerActive) {
				this.outsideHandlerActive = true;
				$(document).on('click touchstart', this.outsideClickHandler);
			}
		},
		hidePopup: function() {
			// hide popup
			this.holder.removeClass(this.options.openClass);
			this.popup.css({
				display: 'none'
			});

			// outside click handler
			if (this.clickMode && this.options.hideOnClickOutside && this.outsideHandlerActive) {
				this.outsideHandlerActive = false;
				$(document).off('click touchstart', this.outsideClickHandler);
			}
		},
		bind: function(f, scope, forceArgs) {
			return function() {
				return f.apply(scope, forceArgs ? [forceArgs] : arguments);
			};
		},
		destroy: function() {
			this.popup.removeAttr('style');
			this.holder.removeClass(this.options.openClass);
			this.btnOpen.add(this.btnClose).add(this.popup).off('.popup');
			$(document).off('click touchstart', this.outsideClickHandler);
		}
	};

	// detect touch devices
	const isTouchDevice = /Windows Phone/.test(navigator.userAgent) || ('ontouchstart' in window) || window.DocumentTouch && document instanceof DocumentTouch;

	// jQuery plugin interface
	$.fn.contentPopup = function(opt) {
		// biome-ignore lint/style/noArguments: <explanation>
		const args = Array.prototype.slice.call(arguments);
		const method = args[0];

		return this.each(function() {
			const $holder = jQuery(this);
			const instance = $holder.data('ContentPopup');

			if (typeof opt === 'object' || typeof opt === 'undefined') {
				$holder.data('ContentPopup', new ContentPopup($.extend({
					holder: this
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