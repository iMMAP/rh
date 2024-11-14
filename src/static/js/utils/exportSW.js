
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

