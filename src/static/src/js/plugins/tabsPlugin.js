/* eslint-disable */
/*
 * jQuery Tabs plugin
 */

; ((($, $win) => {

  function Tabset ($holder, options) {
    this.$holder = $holder;
    this.options = options;

    this.init();
  }

  Tabset.prototype = {
    init: function () {
      this.$tabLinks = this.$holder.find(this.options.tabLinks);

      this.setStartActiveIndex();
      this.setActiveTab();

      if (this.options.autoHeight) {
        this.$tabHolder = $(this.$tabLinks.eq(0).attr(this.options.attrib)).parent();
      }

      this.makeCallback('onInit', this);
    },

    setStartActiveIndex: function () {
      const $classTargets = this.getClassTarget(this.$tabLinks);
      let $activeLink = $classTargets.filter(`.${this.options.activeClass}`);
      const $hashLink = this.$tabLinks.filter(`[${this.options.attrib}="${location.hash}"]`);
      

      if (this.options.checkHash && $hashLink.length) {
        $activeLink = $hashLink;
      }

     const activeIndex = $classTargets.index($activeLink);

      this.activeTabIndex = this.prevTabIndex = (activeIndex === -1 ? (this.options.defaultTab ? 0 : null) : activeIndex);
    },

    setActiveTab: function () {

      this.$tabLinks.each((i, link) => {
        const $link = $(link);
        const $classTarget = this.getClassTarget($link);
        const $tab = $($link.attr(this.options.attrib));

        if (i !== this.activeTabIndex) {
          $classTarget.removeClass(this.options.activeClass);
          $tab.addClass(this.options.tabHiddenClass).removeClass(this.options.activeClass);
        } else {
          $classTarget.addClass(this.options.activeClass);
          $tab.removeClass(this.options.tabHiddenClass).addClass(this.options.activeClass);
        }

        this.attachTabLink($link, i);
      });
    },

    attachTabLink: function ($link, i) {
      const self = this;

      $link.on(`${this.options.event}.tabset`, function (e) {
        e.preventDefault();

        if (self.activeTabIndex === self.prevTabIndex && self.activeTabIndex !== i) {
          self.activeTabIndex = i;
          self.switchTabs();
        }
        if (self.options.checkHash) {
          location.hash = jQuery(this).attr('href').split('#')[1]
        }
      });
    },

    resizeHolder: function (height) {

      if (height) {
        this.$tabHolder.height(height);
        setTimeout(() => {
          this.$tabHolder.addClass('transition');
        }, 10);
      } else {
        this.$tabHolder.removeClass('transition').height('');
      }
    },

    switchTabs: function () {

      const $prevLink = this.$tabLinks.eq(this.prevTabIndex);
      const $nextLink = this.$tabLinks.eq(this.activeTabIndex);

      const $prevTab = this.getTab($prevLink);
      const $nextTab = this.getTab($nextLink);

      $prevTab.removeClass(this.options.activeClass);

      if (this.haveTabHolder()) {
        this.resizeHolder($prevTab.outerHeight());
      }

      setTimeout(() => {
        this.getClassTarget($prevLink).removeClass(this.options.activeClass);

        $prevTab.addClass(this.options.tabHiddenClass);
        $nextTab.removeClass(this.options.tabHiddenClass).addClass(this.options.activeClass);

        this.getClassTarget($nextLink).addClass(this.options.activeClass);

        if (this.haveTabHolder()) {
          this.resizeHolder($nextTab.outerHeight());

          setTimeout(() => {
            this.resizeHolder();
            this.prevTabIndex = this.activeTabIndex;
            this.makeCallback('onChange', this);
          }, this.options.animSpeed);
        } else {
          this.prevTabIndex = this.activeTabIndex;
        }
      }, this.options.autoHeight ? this.options.animSpeed : 1);
    },

    getClassTarget: function ($link) {
      return this.options.addToParent ? $link.parent() : $link;
    },

    getActiveTab: function () {
      return this.getTab(this.$tabLinks.eq(this.activeTabIndex));
    },

    getTab: function ($link) {
      return $($link.attr(this.options.attrib));
    },

    haveTabHolder: function () {
      return this.$tabHolder?.length;
    },

    destroy: function () {
      const self = this;

      this.$tabLinks.off('.tabset').each(function () {
        const $link = $(this);

        self.getClassTarget($link).removeClass(self.options.activeClass);
        $($link.attr(self.options.attrib)).removeClass(`${self.options.activeClass} ${self.options.tabHiddenClass}`);
      });

      this.$holder.removeData('Tabset');
    },

    makeCallback: function (name) {
      if (typeof this.options[name] === 'function') {
        // biome-ignore lint/style/noArguments: <explanation>
        const args = Array.prototype.slice.call(arguments);
        args.shift();
        this.options[name].apply(this, args);
      }
    }
  };

  $.fn.tabset = function (opt) {
    // biome-ignore lint/style/noArguments: <explanation>
    const args = Array.prototype.slice.call(arguments);
    const method = args[0];

    const options = $.extend({
      activeClass: 'active',
      addToParent: false,
      autoHeight: false,
      checkHash: false,
      defaultTab: true,
      animSpeed: 500,
      tabLinks: 'a',
      attrib: 'href',
      event: 'click',
      tabHiddenClass: 'js-tab-hidden'
    }, opt);
    // biome-ignore lint/correctness/noSelfAssign: <explanation>
    options.autoHeight = options.autoHeight;

    return this.each(function () {
      const $holder = jQuery(this);
      const instance = $holder.data('Tabset');

      if (typeof opt === 'object' || typeof opt === 'undefined') {
        $holder.data('Tabset', new Tabset($holder, options));
      } else if (typeof method === 'string' && instance) {
        if (typeof instance[method] === 'function') {
          args.shift();
          instance[method].apply(instance, args);
        }
      }
    });
  };
})(jQuery, jQuery(window)));
