// mobile menu init
export default function initMobileNav() {
	const menuOpener = document.querySelector(".mobile-menu-opener");
	const menuHolder = document.querySelector(".mobile-menu-holder");
	const body = document.body;

	const toggleMenu = () => {
		body.classList.toggle("nav-active");
	};

	const hideMenu = (e) => {
		if (!menuHolder.contains(e.target) && !menuOpener.contains(e.target)) {
			body.classList.remove("nav-active");
		}
	};

	menuOpener.addEventListener("click", (e) => {
		e.preventDefault();
		toggleMenu();
	});

	document.addEventListener("click", hideMenu);
}