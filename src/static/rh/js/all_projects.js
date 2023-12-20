/**
* Ready Function
**/

$(function () {

    $('tr[data-url]').on('click', function(e) {
        const url = $(this).data('url');
        window.location.href = url;
	});

    $('.js_multiselect').select2()

    $('.close-alert-message').on('click', function() {
        $('.message-container').css('display','none');
    });
    // toggle between accordion arrow
    $("#activityAcc").on("click", function(){
        let up =$(".activity-arrow-up");
        let down =$(".activity-arrow-down");
        if(up.hasClass("hidden")){
            up.removeClass("hidden");
            down.addClass("hidden");
        } else {
            up.addClass("hidden");
            down.removeClass("hidden");
        }
    });
    $("#projectAcc").on("click", function(){
        let arrowUp = $(".accordion-arrow-up");
        let arrowDown = $(".accordion-arrow-down");
        
        if(arrowUp.hasClass("hidden")){
            arrowUp.removeClass("hidden");
            arrowDown.addClass("hidden");
        } else {
            arrowUp.addClass("hidden");
            arrowDown.removeClass("hidden");
        }
    });

   

});

// Filter accordion 
const accordionItems = document.querySelectorAll(".accordion-item");
accordionItems.forEach(item =>{
    const title = item.querySelector(".accordion-title");
    const content = item.querySelector(".accordion-content");
    title.addEventListener("click",()=>{
        
        for(let i = 0; i<accordionItems.length; i++){
            if(accordionItems[i] != item){
                accordionItems[i].classList.remove("active");
            } else {item.classList.toggle("active");}
        } 
    });
    
});

