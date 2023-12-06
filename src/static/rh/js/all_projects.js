/**
* Ready Function
**/

$(function () {

    $('tr[data-url]').on('click', function(e) {
        const url = $(this).data('url');
        window.location.href = url;
	});
    
});

const accHandler = document.querySelector(".project-accordion-handler");
let arrowUp = document.querySelector(".accordion-arrow-up");
let arrowDown = document.querySelector(".accordion-arrow-down");
arrowUp.classList.add("hidden");
accHandler.addEventListener("click", function(){

    let content = document.querySelector(".project-accContainer");
    content.classList.toggle("hidden");
    if(arrowUp.classList.contains("hidden")){
        arrowDown.classList.add("hidden");
        arrowUp.classList.remove("hidden");
        
    } else {
        arrowDown.classList.remove("hidden");
        arrowUp.classList.add("hidden");
    }
    
});
const activityAccordion = document.querySelector(".activity-accordion-handler");
let accarrowUp = document.querySelector(".activity-arrow-up");
let accarrowDown = document.querySelector(".activity-arrow-down");
accarrowUp.classList.add("hidden");
activityAccordion.addEventListener("click", function(){

    let content = document.querySelector(".activity-accContainer");
    content.classList.toggle("hidden");
    if(accarrowUp.classList.contains("hidden")){
        accarrowDown.classList.add("hidden");
        accarrowUp.classList.remove("hidden");
      
    } else {
        accarrowDown.classList.remove("hidden");
        accarrowUp.classList.add("hidden");
    }
    
});