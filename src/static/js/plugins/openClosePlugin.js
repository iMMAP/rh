/* eslint-disable */

/*
 * jQuery Open/Close plugin
 */
;((($) => {
	function OpenClose(options) {
		this.options = $.extend({
			addClassBeforeAnimation: true,
			hideOnClickOutside: false,
			activeClass: 'active',
			opener: '.opener',
			slider: '.slide',
			animSpeed: 400,
			effect: 'fade',
			event: 'click'
		}, options);
		this.init();
	}
	OpenClose.prototype = {
		init: function() {
			if (this.options.holder) {
				this.findElements();
				this.attachEvents();
				this.makeCallback('onInit', this);
			}
		},
		findElements: function() {
			this.holder = $(this.options.holder);
			this.opener = this.holder.find(this.options.opener);
			this.slider = this.holder.find(this.options.slider);
		},
		attachEvents: function() {
			this.eventHandler = (e) => {
				e.preventDefault();
				if (this.slider.hasClass(slideHiddenClass)) {
					this.showSlide();
				} else {
					this.hideSlide();
				}
			};
      this.slider.attr('aria-hidden', 'true');
      this.opener.attr('aria-expanded', 'false');
			this.opener.on(this.options.event, this.eventHandler);

			// hover mode handler
			if (this.options.event === 'hover') {
				this.opener.on('mouseenter', () => {
					if (!this.holder.hasClass(this.options.activeClass)) {
						this.showSlide();
					}
				});
				this.holder.on('mouseleave', () => {
					this.hideSlide();
				});
			}

			// outside click handler
			this.outsideClickHandler = (e) => {
				if (this.options.hideOnClickOutside) {
					const target = $(e.target);
					if (!target.is(this.holder) && !target.closest(this.holder).length) {
						this.hideSlide();
					}
				}
			};

			// set initial styles
			if (this.holder.hasClass(this.options.activeClass)) {
				$(document).on('click touchstart', this.outsideClickHandler);
			} else {
				this.slider.addClass(slideHiddenClass);
			}
		},
		showSlide: function() {
			if (this.options.addClassBeforeAnimation) {
				this.holder.addClass(this.options.activeClass);
			}
      this.slider.attr('aria-hidden', 'false');
      this.opener.attr('aria-expanded', 'true');
			this.slider.removeClass(slideHiddenClass);
			$(document).on('click touchstart', this.outsideClickHandler);

			this.makeCallback('animStart', true);
			toggleEffects[this.options.effect].show({
				box: this.slider,
				speed: this.options.animSpeed,
				complete: () => {
					if (!this.options.addClassBeforeAnimation) {
						this.holder.addClass(this.options.activeClass);
					}
					this.makeCallback('animEnd', true);
				}
			});
		},
		hideSlide: function() {
			if (this.options.addClassBeforeAnimation) {
				this.holder.removeClass(this.options.activeClass);
			}
			$(document).off('click touchstart', this.outsideClickHandler);

			this.makeCallback('animStart', false);
			toggleEffects[this.options.effect].hide({
				box: this.slider,
				speed: this.options.animSpeed,
				complete: () => {
					if (!this.options.addClassBeforeAnimation) {
						this.holder.removeClass(this.options.activeClass);
					}
					this.slider.addClass(slideHiddenClass);
          this.slider.attr('aria-hidden', 'true');
          this.opener.attr('aria-expanded', 'false');
					this.makeCallback('animEnd', false);
				}
			});
		},
		destroy: function() {
			this.slider.removeClass(slideHiddenClass).css({
				display: ''
			});
			this.opener.off(this.options.event, this.eventHandler);
			this.holder.removeClass(this.options.activeClass).removeData('OpenClose');
			$(document).off('click touchstart', this.outsideClickHandler);
		},
		makeCallback: function(name) {
			if (typeof this.options[name] === 'function') {
				// biome-ignore lint/style/noArguments: <explanation>
				const args = Array.prototype.slice.call(arguments);
				args.shift();
				this.options[name].apply(this, args);
			}
		}
	};

	// add stylesheet for slide on DOMReady
	const slideHiddenClass = 'js-slide-hidden';
	((() => {
		const tabStyleSheet = $('<style type="text/css">')[0];
		let tabStyleRule = `.${slideHiddenClass}`;
		tabStyleRule += '{position:absolute !important;left:-9999px !important;top:-9999px !important;display:block !important}';
		if (tabStyleSheet.styleSheet) {
			tabStyleSheet.styleSheet.cssText = tabStyleRule;
		} else {
			tabStyleSheet.appendChild(document.createTextNode(tabStyleRule));
		}
		$('head').append(tabStyleSheet);
	})());

	// animation effects
	const toggleEffects = {
		slide: {
			show: (o) => {
				o.box.stop(true).hide().slideDown(o.speed, o.complete);
			},
			hide: (o) => {
				o.box.stop(true).slideUp(o.speed, o.complete);
			}
		},
		fade: {
			show: (o) => {
				o.box.stop(true).hide().fadeIn(o.speed, o.complete);
			},
			hide: (o) => {
				o.box.stop(true).fadeOut(o.speed, o.complete);
			}
		},
		none: {
			show: (o) => {
				o.box.hide().show(0, o.complete);
			},
			hide: (o) => {
				o.box.hide(0, o.complete);
			}
		}
	};

	// jQuery plugin interface
	$.fn.openClose = function(opt) {
		// biome-ignore lint/style/noArguments: <explanation>
		const args = Array.prototype.slice.call(arguments);
		const method = args[0];

		return this.each(function() {
			const $holder = jQuery(this);
			const instance = $holder.data('OpenClose');

			if (typeof opt === 'object' || typeof opt === 'undefined') {
				$holder.data('OpenClose', new OpenClose($.extend({
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