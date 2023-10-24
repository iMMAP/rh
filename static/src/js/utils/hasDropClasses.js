// add classes if item has dropdown
export default function initDropDownClasses() {
	jQuery('.main-nav li').each(function() {
		var item = jQuery(this);
		var drop = item.find('ul');
		var link = item.find('a').eq(0);
		if (drop.length) {
			item.addClass('has-drop-down js-main-nav-openclose');
			if (link.length) link.addClass('openclose-opener');
		}
	});
}
