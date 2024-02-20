$(function () {
	const isHrpProject = $("#id_is_hrp_project");
	const hasHrpCode = $("#id_has_hrp_code");
	const prHasHRPCodeEl = $("#prHasHRPCodeEl");
	const prHrpCode = $("#prHrpCode");
	const idHrpCode = $("#id_hrp_code");

	/**
	 * Toggles the display of the HRP code form field based on whether the 'isHrpProject'
	 * checkbox is checked or not. If checked, the HRP code form field and corresponding
	 * label are displayed. Otherwise, the HRP code field is hidden, its value is reset,
	 * and the 'hasHrpCode' checkbox is unchecked.
	 */
	function toggleHrpCode() {
		if (isHrpProject.is(":checked")) {
			prHasHRPCodeEl.show(300);
		} else {
			prHrpCode.hide(200);
			idHrpCode.val("");
			prHasHRPCodeEl.hide(200);
			hasHrpCode.prop("checked", false);
		}
	}

	/**
	  * Toggles the "required" attribute and "is-required" class of the project HRP code field
		based on whether the "has HRP code" checkbox is checked or not.
	  * If the checkbox is checked, the HRP code field is shown,
		made required and the "is-required" class is added.
	  * If the checkbox is unchecked, the HRP code field is hidden,
		its value is cleared, the "required" attribute is removed, and the "is-required" class is removed.
	  */
	function toggleRequired() {
		if (hasHrpCode.is(":checked")) {
			prHrpCode.show(300);
			prHrpCode.prop("required", true);
			prHrpCode.addClass("is-required");
		} else {
			prHrpCode.hide(200);
			idHrpCode.val("");
			prHrpCode.prop("required", false);
			prHrpCode.removeClass("is-required");
		}
	}

	toggleHrpCode();
	toggleRequired();
	isHrpProject.on("change", function() {toggleHrpCode()});
	hasHrpCode.on("change", function() {toggleRequired()});

	// Define a function to calculate the budget gap
	function calculateBudgetGap() {
		// Get the values of the budget and budget received fields
		var budget = parseFloat($("#id_budget").val());
		var budgetReceived = parseFloat($("#id_budget_received").val());
		if(budgetReceived > budget){
			$("#budget_received_message").text("The received budget can not be more than the whole budget !!");
			$("#budget_received_message").css("color","red");
			$("#id_budget_received").val(budget);
			$("#id_budget_received").attr("max",budget);
			$("#id_budget_gap").val(0);
			setTimeout(() => {
				$("#budget_received_message").text("");
			}, 3000);
		} else {
			// Calculate the budget gap
		var budgetGap = budget - budgetReceived;

		// Set the value of the budget gap field
		$("#id_budget_gap").val(budgetGap.toFixed(0));
		}
		
	}

	// Attach the function to the change event of the budget and budget received fields
	$("#id_budget, #id_budget_received").on("input", calculateBudgetGap);
	

	function get_activity_domains() {
		const domainsUrl = $("#id_activity_domains").attr("activity-domains-queries-url");
		const domainsIds = $("#id_activity_domains option")
			.map(function () {
				return $(this).val();
			})
			.get();

		const clusterIds = $("#id_clusters").val();
		const selectedDomains = $("#id_activity_domains").val();

		const requestData = {
			clusters: clusterIds,
			listed_domains: domainsIds,
		};

		// Use JavaScript Cookie library
		const csrftoken = Cookies.get('csrftoken');

		$.ajax({
			type: "POST",
			url: domainsUrl,
			data: requestData,
			beforeSend: function(xhr, settings) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			},
			success: function (data) {
				const $domains = $("#id_activity_domains");
				$domains.html(data);
				$domains.val(selectedDomains);
			},
		});
	}

	// Run when updating a new project
	if (window.location.pathname.includes("update")) {
		get_activity_domains();
	}
	
	$("#id_clusters").on("change", function() {
		get_activity_domains();
	})

});
const activityAcc = document.querySelector('#activityAcc')
if(activityAcc){
    activityAcc.addEventListener('click', function () {
    let up = document.querySelector('.activity-arrow-up');
    let down = document.querySelector('.activity-arrow-down');

    if (up.classList.contains('hidden')) {
        up.classList.remove('hidden');
        down.classList.add('hidden');
    } else {
        up.classList.add('hidden');
        down.classList.remove('hidden');
    }
});
}   

document.getElementById('projectAcc').addEventListener('click', function () {
        let arrowUp = document.querySelector('.accordion-arrow-up');
        let arrowDown = document.querySelector('.accordion-arrow-down');

        if (arrowUp.classList.contains('hidden')) {
            arrowUp.classList.remove('hidden');
            arrowDown.classList.add('hidden');
        } else {
            arrowUp.classList.add('hidden');
            arrowDown.classList.remove('hidden');
        }
    });
// Filter accordion 
const accordionItems = document.querySelectorAll(".accordion-item");
accordionItems.forEach(item =>{
    const title = item.querySelector(".accordion-title");
    const content = item.querySelector(".accordion-content");
    title.addEventListener("click",()=>{
        console.log("clicked");
        for(let i = 0; i<accordionItems.length; i++){
            if(accordionItems[i] != item){
                accordionItems[i].classList.remove("active");
            } else {item.classList.toggle("active");}
        } 
    });
    
});
