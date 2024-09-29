// accordion menu init
export default function initOpenClose() {
	const holders = document.querySelectorAll(".js-main-nav-openclose");

	holders.forEach((holder) => {
		const opener = holder.querySelector(".openclose-opener");
		const slider = holder.querySelector(".inner-drop");
		const activeClass = "active";
		const slideHiddenClass = "js-slide-hidden";
		const animSpeed = 400;

    const showSlide = () => {
					holder.classList.add(activeClass);
					slider.setAttribute("aria-hidden", "false");
					slider.classList.remove(slideHiddenClass);
					slider.style.transition = `height ${animSpeed}ms`;
					slider.style.height = `${slider.scrollHeight}px`;
				};

	const hideSlide = () => {
			holder.classList.remove(activeClass);
			slider.setAttribute("aria-hidden", "true");
			slider.style.transition = `height ${animSpeed}ms`;
			slider.style.height = "0";
			setTimeout(() => {
				slider.classList.add(slideHiddenClass);
			}, animSpeed);
		};

		opener.addEventListener("click", (e) => {
			e.preventDefault();
			if (slider.classList.contains(slideHiddenClass)) {
				showSlide();
			} else {
				hideSlide();
			}
		});

		document.addEventListener("click", (e) => {
			if (
				!holder.contains(e.target) &&
				holder.classList.contains(activeClass)
			) {
				hideSlide();
			}
		});

		// Initial setup
		slider.classList.add(slideHiddenClass);
		slider.style.height = "0";
		slider.setAttribute("aria-hidden", "true");
		opener.setAttribute("aria-expanded", "false");
	});
}