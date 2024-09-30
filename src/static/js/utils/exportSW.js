document.querySelectorAll(".input-check").forEach((element) => {
	element.addEventListener("click", () => {
		checkboxCounter();
	});
});

try {
	const all_checks = document.querySelectorAll(".select-all");
	const project_checkbox = document.querySelectorAll(".project-check");
	const activity_checkbox = document.querySelectorAll(".activity-check");
	const location_checkbox = document.querySelectorAll(".targetlocation-check");
	all_checks.forEach((checkElement) => {
		checkElement?.addEventListener("click", (e) => {
			let checkElementId = e.target.id;
			let checkbox_array = new Array();
			let condition = true;
			if (checkElement.checked) {
				if (checkElementId === "project-plan") {
					checkbox_array = project_checkbox;
					condition = true;
				} else if (checkElementId === "activity-plan") {
					checkbox_array = activity_checkbox;
					condition = true;
				} else if (checkElementId === "target-location") {
					checkbox_array = location_checkbox;
					condition = true;
				}
				checkboxManager(checkbox_array, condition);
			} else if (checkElement.checked == false) {
				if (checkElementId === "project-plan") {
					checkbox_array = project_checkbox;
					condition = false;
				} else if (checkElementId === "activity-plan") {
					checkbox_array = activity_checkbox;
					condition = false;
				} else if (checkElementId === "target-location") {
					checkbox_array = location_checkbox;
					condition = false;
				}
				checkboxManager(checkbox_array, condition);
			}
		});
	});
} catch {}

function checkboxManager(checkboxes, condition) {
	checkboxes.forEach((checkElement) => {
		checkElement.checked = condition;
		checkElement.style.accentColor = "#a52824";
	});
	checkboxCounter();
}
function checkboxCounter() {
	const checkboxes = document.querySelectorAll(".input-check");
	const checkedCounterElement = document.getElementById("selectedCount");
	let checkedCounter = 0;
	let uncheckedCounter = 0;
	checkboxes.forEach((checkbox) => {
		if (checkbox.checked == true) {
			checkedCounter++;
		} else if (checkbox.checked == false) {
			uncheckedCounter++;
		}
	});
	checkedCounterElement.textContent = checkedCounter;
}

//Reset the checkbox
document.querySelector("#resetFilterButton")?.addEventListener("click", () => {
	const checkboxes = document.querySelectorAll("input[type=checkbox]:checked");
	const countSpan = document.querySelector("#selectedCount");
	checkboxes.forEach((checkbox) => {
		checkbox.checked = false;
	});
	document.querySelector("#not-checked-message").textContent = "All clear !";
	setTimeout(() => {
		document.querySelector("#not-checked-message").textContent = "";
	}, 3000);
	checkboxCounter();
});

document.querySelector(".export-button")?.addEventListener("click",(event) => {
	event.preventDefault();
	event.stopPropagation();
	// Get the export URL from the button's data-url attribute
	const exportUrl = event.target.closest("a").getAttribute("data-url");

	// Send an AJAX request to the export URL
	fetch(exportUrl, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrftoken,
		},
		body: JSON.stringify({ csrfmiddlewaretoken: csrftoken }),
	})
	.then(response => response.json())
	.then(response => {
		// Create a temporary download link and click it to trigger the file download
		const link = document.createElement("a");
		link.href = response.file_url;
		link.download = response.file_name;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	})
	.catch((error) => {
		if (error.status === 400) {
			console.log("Error: No records selected for export");
		} else {
			console.log(`Error: ${error.message}`);
		}
	});
});

// filter the project field and download start
document
	.querySelector("#downloadFilterForm")
	?.addEventListener("click", function (e) {
		e.preventDefault();
		e.stopPropagation();

		const currentDate = new Date();
		const day = currentDate.getDate();
		const month = currentDate.getMonth() + 1; // Month is zero-based
		const year = currentDate.getFullYear();
		const todayDate = `${year}-${month}-${day}`;
		const filename = `custom_project_export_${todayDate}.csv`;

		const routeUrl = this.dataset.url;
		const fileFormat = document.querySelector(
			"input[type=radio]:checked",
		)?.value;

		if (fileFormat) {
			const selectedFieldList = {};
			const checkedFields = document.querySelectorAll(".input-check");
			checkedFields.forEach((field) => {
				if (field.checked) {
					selectedFieldList[field.name] = field.value;
				}
			});
			selectedFieldList.format = fileFormat;

			fetch(routeUrl, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrftoken,
				},
				body: JSON.stringify({ exportData: selectedFieldList }),
			})
				.then((response) => response.json())
				.then((response) => {
					if (fileFormat === "xlsx") {
						const link = document.createElement("a");
						link.href = response.file_url;
						link.download = response.file_name;
						document.body.appendChild(link);
						link.click();
						document.body.removeChild(link);
					} else if (fileFormat === "csv") {
						const url = window.URL.createObjectURL(new Blob([response]));
						const a = document.createElement("a");
						a.style.display = "none";
						a.href = url;
						a.download = filename;
						document.body.appendChild(a);
						a.click();
						window.URL.revokeObjectURL(url);
					}
				})
				.catch((error) => {
					alert(`Something went wrong! ${error}`);
				});
		} else {
			document.querySelector(".file-format-error").style.display = "block";
		}
	});

document.querySelector(".radio-select")?.addEventListener("click", function (e) {
	e.preventDefault();
	e.stopPropagation();
	const url_link = this.getAttribute("data-url");
	console.log(url_link);
	const project_list = [];
	const projectID = document.querySelector(".project-checkbox");
	for (let i = 0; i < projectID.length; i++) {
		if (projectID.is(":checked")) {
			project_list.push(projectID[i].value);
		}
	}
	fetch(url_link, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrftoken,
		},
		body: JSON.stringify({
			projectList: project_list,
			csrfmiddlewaretoken: csrftoken,
		}),
	})
		.then((response) => response.json())
		.then((data) => console.log(data))
		.catch((error) => console.error("Error:", error));
});
// bulk export fetch request
function exportButton(event) {
	event.preventDefault();
	// getting export url
	const export_url = event.currentTarget.dataset.exportUrl;
	const fileFormat = event.currentTarget.dataset.exportFormat;
	const downloadButton = document.querySelector(".export-open");
	const downloading_spinner = document.querySelector(".downloading");
	const icon_downloading = document.querySelector(".icon-download");

	// create filename
	const currentDate = new Date();
	// Extract date components
	const day = currentDate.getDate();
	const month = currentDate.getMonth() + 1; // Month is zero-based
	const year = currentDate.getFullYear();
	// Format the date as needed (example: DD/MM/YYYY)
	const todayDate = `${year}-${month}-${day}`;
	// write the file name
	const filename = `projects_bulk_export_${todayDate}`;

	downloadButton.setAttribute("disabled", "disabled");
	downloading_spinner.style.display = "inline-block";
	icon_downloading.style.display = "none";

	const selected_project_list = [];
	const selectedProject = document.querySelectorAll(".project-checkbox");
	for (let i = 0; i < selectedProject.length; i++) {
		if (selectedProject[i].checked) {
			selected_project_list.push(selectedProject[i].value);
		}
	}
	fetch(export_url, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrftoken,
		},
		body: JSON.stringify(selected_project_list),
	})
		.then((response) => {
			console.log(response);
			if (response.status === 200 && response.ok === true) {
				if (fileFormat === "csv" || fileFormat === "json") {
					return response.blob();
				}
				if (fileFormat === "xlsx") {
					return response.json();
				}
				throw Error("Unsupported file format");
			}
			alert(
				"You don’t have the necessary permissions to complete this action.",
			);
			throw "Permission Denied";
		})
		.then((data) => {
			if (fileFormat === "csv" || fileFormat === "json") {
				const url = window.URL.createObjectURL(data);
				const link = document.createElement("a");
				link.href = url;
				link.download = `${filename}.${fileFormat}`;
				document.body.appendChild(link);
				link.click();
				document.body.removeChild(link);
				window.URL.revokeObjectURL(url);
			} else if (fileFormat === "xlsx") {
				const link = document.createElement("a");
				link.href = data.file_url; // Use the base64-encoded URL
				link.download = data.file_name; // Set the filename for download
				// Append the link to the body, click it to start download, and then remove it
				document.body.appendChild(link);
				link.click();
				document.body.removeChild(link);
			}
		})
		.catch((error) => {
			console.error("Error downloading:", error);
		})
		.finally(() => {
			downloadButton.setAttribute("disabled", "false");
			downloading_spinner.style.display = "none";
			icon_downloading.style.display = "inline-block";
		});
}

try {
	// Export monthly report
	// Export monthly report
	document
		.querySelector(".export-monthly-report")
		?.addEventListener("click", (e) => {
			e.preventDefault();
			// handle the spinner icon
			const downloadIcon = document.querySelector(".icon-download");
			const downloading = document.querySelector(".downloading");
			const download_button = e.currentTarget;
			download_button.setAttribute("disabled", "disabled");
			downloading.style.display = "inline";
			downloadIcon.style.display = "none";
			// get the filter criteria
			const start_data = e.currentTarget.dataset.fieldFrom;
			const end_data = e.currentTarget.dataset.fieldTo;
			const export_url = e.currentTarget.dataset.requestUrl;

			const formData = new FormData();
			formData.append("start_date", start_data);
			formData.append("end_date", end_data);
			formData.append("csrfmiddlewaretoken", csrftoken);
			console.log(formData);
			fetch(export_url, {
				method: "POST",
				body: formData,
			}).then((response) =>
				response
					.json()
					.then((response) => {
						const link = document.createElement("a");
						link.href = response.file_url;
						link.download = response.file_name;
						document.body.appendChild(link);
						link.click();
						document.body.removeChild(link);
					})
					.catch((error) => {
						console.log(error);
					})
					.finally(() => {
						download_button.setAttribute("disabled", "false");
						downloading.style.display = "none";
						downloadIcon.style.display = "inline";
					}),
			);
		});
} catch {}
