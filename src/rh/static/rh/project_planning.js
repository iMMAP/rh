const isHrpProject = document.getElementById("id_is_hrp_project");
const hasHrpCode = document.getElementById("id_has_hrp_code");
const prHasHRPCodeEl = document.getElementById("prHasHRPCodeEl");
const prHrpCode = document.getElementById("prHrpCode");
const idHrpCode = document.getElementById("id_hrp_code");

/**
 * Toggles the display of the HRP code form field based on whether the 'isHrpProject'
 * checkbox is checked or not. If checked, the HRP code form field and corresponding
 * label are displayed. Otherwise, the HRP code field is hidden, its value is reset,
 * and the 'hasHrpCode' checkbox is unchecked.
 */
function toggleHrpCode() {
	if (isHrpProject.checked) {
		prHasHRPCodeEl.style.display = "block";
	} else {
		prHrpCode.style.display = "none";
		idHrpCode.value = "";
		prHasHRPCodeEl.style.display = "none";
		hasHrpCode.checked = false;
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
	if (hasHrpCode.checked) {
		prHrpCode.style.display = "block";
		prHrpCode.required = true;
		prHrpCode.classList.add("is-required");
	} else {
		prHrpCode.style.display = "none";
		idHrpCode.value = "";
		prHrpCode.required = false;
		prHrpCode.classList.remove("is-required");
	}
}

	toggleHrpCode();
    toggleRequired();
    isHrpProject.addEventListener("change", toggleHrpCode);
    hasHrpCode.addEventListener("change", toggleRequired);;

// Define a function to calculate the budget gap
function calculateBudgetGap() {
        const budget = Number.parseFloat(document.getElementById("id_budget").value);
        const budgetReceived = Number.parseFloat(document.getElementById("id_budget_received").value);
        if (budgetReceived > budget) {
            document.getElementById("budget_received_message").textContent = "The received budget can not be more than the whole budget !!";
            document.getElementById("budget_received_message").style.color = "red";
            document.getElementById("id_budget_received").value = budget;
            document.getElementById("id_budget_received").setAttribute("max", budget);
            document.getElementById("id_budget_gap").value = 0;
            setTimeout(() => {
                document.getElementById("budget_received_message").textContent = "";
            }, 3000);
        } else {
            const budgetGap = budget - budgetReceived;
            document.getElementById("id_budget_gap").value = budgetGap.toFixed(0);
        }
    }
// Attach the function to the change event of the budget and budget received fields
document
	.getElementById("id_budget")
	.addEventListener("input", calculateBudgetGap);
document
	.getElementById("id_budget_received")
	.addEventListener("input", calculateBudgetGap);

const choice = new Choices("#id_activity_domains", {
	searchEnabled: true,
	itemSelectText: "",
	removeItemButton: true,
	classNames: {
		listDropdown: "choices__list--dropdown",
	},
	shouldSort: false,
});

function get_activity_domains() {
	const domainsUrl = document
		.getElementById("id_activity_domains")
		.getAttribute("activity-domains-queries-url");


	const domainsIds = Array.from(
		document.querySelectorAll("#id_activity_domains option"),
	).map((option) => option.value);

	const clusterIds = Array.from(document.getElementById("id_clusters").options).filter(option => option.selected).map(option => Number.parseInt(option.value));

	const requestData = {
		clusters: clusterIds,
		listed_domains: domainsIds,
	};

	fetch(domainsUrl, {
		method: "POST",
		body: JSON.stringify(requestData),
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrftoken,
		},
	})
		.then((response) => response.json())
		.then((data) => {
			choice.setChoices(data, "value", "label", true);
		});
}

// Run when updating a new project
if (window.location.pathname.includes("update")) {
	get_activity_domains();
}

document.getElementById("id_clusters").addEventListener("change", get_activity_domains);