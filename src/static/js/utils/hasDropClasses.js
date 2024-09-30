// add classes if item has dropdown
export default function initDropDownClasses() {
	document.querySelectorAll('.main-nav li').forEach((item) => {
		const drop = item.querySelector('ul');
		const link = item.querySelector('a');

		if (drop) {
			item.classList.add('has-drop-down', 'js-main-nav-openclose');
			if (link) link.classList.add('openclose-opener');
		}
	});
}
