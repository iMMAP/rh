const isHrpProject = document.getElementById("id_is_hrp_project");
const prHrpCode = document.getElementById("prHrpCode");
const idHrpCode = document.getElementById("id_hrp_code");

document.querySelector(".end-date").addEventListener("change", (e) => {
	const end_date = e.target.value;
	const start_date = document.querySelector(".start-date");

	if (start_date.value > end_date) {
		document.getElementById("date-validation-error").style.display =
			"inline-block";
		e.target.value = null;
	}
});

/**
 * Toggles the display of the HRP code form field based on whether the 'isHrpProject'
 * checkbox is checked or not. If checked, the HRP code form field and corresponding
 * label are displayed. Otherwise, the HRP code field is hidden, its value is reset,
 * and the 'hasHrpCode' checkbox is unchecked.
 */
function toggleHrpCode() {
	if (isHrpProject.checked) {
		prHrpCode.style.display = "block";
	} else {
		prHrpCode.style.display = "none";
		idHrpCode.value = "";
	}
}

toggleHrpCode();
isHrpProject.addEventListener("change", toggleHrpCode);

// Define a function to calculate the budget gap
function calculateBudgetGap() {
	const budget = Number.parseFloat(document.getElementById("id_budget").value);
	const budgetReceived = Number.parseFloat(
		document.getElementById("id_budget_received").value,
	);
	if (budgetReceived > budget) {
		document.getElementById("budget_received_message").textContent =
			"The received budget can not be more than the whole budget !!";
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

const choiceOptions = {
	searchEnabled: true,
	itemSelectText: "",
	removeItemButton: true,
	resetScrollPosition: false,
	classNames: {
		listDropdown: "choices__list--dropdown",
	},
	shouldSort: false,
};

const userChoice = new Choices("#id_user", choiceOptions);
const activityDomainChoice = new Choices("#id_activity_domains", choiceOptions);
const donorChoice = new Choices("#id_donors", choiceOptions);
const clusterChoice = new Choices("#id_clusters", choiceOptions);
const iPChoice = new Choices("#id_implementing_partners", choiceOptions);
const pPChoice = new Choices("#id_programme_partners", choiceOptions);

function get_activity_domains() {
	const domainsUrl = document
		.getElementById("id_activity_domains")
		.getAttribute("activity-domains-queries-url");

	const domainsIds = Array.from(
		document.querySelectorAll("#id_activity_domains option"),
	).map((option) => option.value);

	const clusterIds = Array.from(document.getElementById("id_clusters").options)
		.filter((option) => option.selected)
		.map((option) => Number.parseInt(option.value));

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
			// choice.removeActiveItems()
			activityDomainChoice.setChoices(data, "value", "label", true);
		});
}

// Run when updating a new project
if (window.location.pathname.includes("update")) {
	get_activity_domains();
}

clusterChoice.passedElement.element.addEventListener(
	"change",
	get_activity_domains,
);

clusterChoice.passedElement.element.addEventListener("removeItem", (e) => {
	for (const element of activityDomainChoice.getValue()) {
		if (
			Number.parseInt(element?.customProperties?.clusterId) ===
			Number.parseInt(e.detail.value)
		) {
			activityDomainChoice.removeActiveItemsByValue(element.value);
		} else if (element.groupId === -1){
			activityDomainChoice.removeActiveItemsByValue(element.value);
		}
	}
});
