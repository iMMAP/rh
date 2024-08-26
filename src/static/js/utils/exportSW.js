
// changing the checkbox color when it checked
$("input[type=checkbox]").change(function () {
	$(this).css("accent-color", "#af4745");
});
// count the number of checkbox selected for export
try{
	const checkedField = document.querySelectorAll(".input-check");
	document.getElementById("totalCount").innerHTML=checkedField.length;
	const countSpan = document.getElementById("selectedCount");
	let selectedCount = 0;
	checkedField.forEach(field => {
		field.addEventListener("click", () =>{
			if(field.checked == true){
				selectedCount++;
			} else if(field.checked == false){
				selectedCount--;
			}
			countSpan.textContent = selectedCount;
		})
		countSpan.textContent = selectedCount;
	});
}catch{}


//Reset the checkbox
$("#resetFilterButton").on("click", () => {
	const checkbox = $("input[type=checkbox]");
	const countSpan = $("#selectedCount");
	if (checkbox.is(":checked")) {
		checkbox.prop("checked", false);
	} else {
		$("#not-checked-message").text("All clear !");
		setTimeout(() => {
			$("#not-checked-message").text("");
		}, 3000);
	}
	let selectedCount = 0;
	countSpan.text(selectedCount);

	
});

$("tr[data-url]").click(function () {
	window.location.href = $(this).data("url");
});

$(".export-button").click(function (event) {
	event.preventDefault();
	event.stopPropagation();
	// Get the export URL from the button's data-url attribute
	const exportUrl = $(this).find("a").data("url");

	// Send an AJAX request to the export URL
	$.ajax({
		url: exportUrl,
		method: "POST",
		data: {
			csrfmiddlewaretoken: csrftoken,
		},
		success: (response) => {
			// Create a temporary download link and click it to trigger the file download
			const link = document.createElement("a");
			link.href = response.file_url;
			link.download = response.file_name;
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
		},
		error: (xhr, status, error) => {
			if (xhr.status === 400) {
				console.log("Error: No records selected for export");
			} else {
				console.log(`Error: ${xhr.responseText}`);
			}
		},
	});
});
// filter the project field and download start
$("#downloadFilterForm").click(function (e) {
	e.preventDefault();
	e.stopPropagation();
	
	let currentDate = new Date();
	// Extract date components
	let day = currentDate.getDate();
	let month = currentDate.getMonth() + 1; // Month is zero-based
	let year = currentDate.getFullYear();
	// Format the date as needed (example: DD/MM/YYYY)
	let todayDate = year+'-'+month+'-'+day;
	// write the file name
	let filename = "custom_project_export_"+todayDate+".csv";

	// get the url
	const routeUrl = $(this).find("a").data("url");
	const file_format = $("input[type=radio]:checked").val();
	if(file_format){
		// create empty list
		const selectedFieldList = {};
		// get the selected fields and store it in the list
		const checkedField = document.querySelectorAll(".input-check");
		for (let i = 0; i < checkedField.length; i++) {
			if (checkedField[i].checked === true) {
				selectedFieldList[checkedField[i].name] = checkedField[i].value;
			}
		}
		selectedFieldList.format = file_format;
		// create post request
		$.post({
			url: routeUrl,
			method: "POST",
			data: {
				exportData: JSON.stringify(selectedFieldList),
				csrfmiddlewaretoken: csrftoken,
			},
			success: (response) => {
				if(file_format == 'xlsx'){
				const link = document.createElement("a");
				link.href = response.file_url;
				link.download = response.file_name;
				document.body.appendChild(link);
				link.click();
				document.body.removeChild(link);
				} else if (file_format == 'csv') {
					response.blob
					const url = window.URL.createObjectURL(new Blob([response]));
					const $a = $('<a style="display: none;"></a>');
					$a.attr('href', url);
					$a.attr('download', filename);
					$('body').append($a);
					$a[0].click();
					window.URL.revokeObjectURL(url);
				}
			},
			error: (error) => {
				swal(`Something went wrong! ${error}`);
			},
	});
	} else {
		$(".file-format-error").css("display","block");
	}
});

//filter the project field and download
function showConfirmModal(event) {
	// Prevent the default behavior of the click event
	event.preventDefault();
	event.stopPropagation();

	// Get the relevant data attributes from the clicked element
	const dataURL = event.currentTarget.dataset.url;
	let returnURL = event.currentTarget.dataset.returnUrl;
	const name = event.currentTarget.dataset.recordName;
	const popupType = event.currentTarget.dataset.type;

	// Initialize variables to be used in the SweetAlert2 modal
	let title;
	let text;
	let icon;
	let dangerMode;
	let successMessage;

	// Set the modal variables based on the type of popup requested
	if (popupType === "copy") {
		title = `Are you sure you want to duplicate ${name}?`;
		text = "";
		icon = "warning";
		dangerMode = true;
		successMessage = `Done! ${name} has been duplicated successfully!`;
	} else if (popupType === "delete") {
		title = `Are you sure you want to delete this ${name}?`;
		text = "Once deleted, you will not be able to recover this record!";
		icon = "warning";
		dangerMode = true;
		successMessage = `Done! ${name} has been deleted successfully!`;
	} else if (popupType === "archive") {
		title = `Are you sure you want to archive ${name}?`;
		text =
			"Archiving the selected record will deactivate it and make it unavailable to users. Please contact the administrator if you need to access the archived records in the future!";
		icon = "warning";
		dangerMode = true;
		successMessage = `Done! ${name} has been archived successfully!`;
	} else if (popupType === "unarchive") {
		title = `Are you sure you want to unarchive ${name}?`;
		text = "Unarchiving the selected record will be reactivate in draft state.";
		icon = "warning";
		dangerMode = true;
		successMessage = `Done! ${name} has been unarchived successfully!`;
	}

	// Display the SweetAlert2 modal with the appropriate variables
	swal({
		title: title,
		text: text,
		icon: icon,
		buttons: true,
		dangerMode: dangerMode,
	}).then((willDelete) => {
		// If the user confirms the action in the modal, send an AJAX request
		if (willDelete) {
			$.ajax({
				method: "GET",
				url: dataURL,
				success: (data) => {
					// If the AJAX request is successful, display a success message and redirect
					if (data.success) {
						swal(successMessage, {
							icon: "success",
						}).then(() => {
							if (popupType === "copy") {
								if (data.returnURL) {
									returnURL = data.returnURL;
								}
							}
							window.location.href = returnURL;
						});
					}
				},
				error: (error_data) => {
					// If the AJAX request fails, display an error message
					swal(`Something went wrong! ${error_data}`);
				},
			});
		}
	});
}

// Attach the click event listener to all elements with class "show_confirm"
$(".show_confirm").click(showConfirmModal);

$(".radio-select").on("click", function (e) {
	e.preventDefault();
	e.stopPropagation();
	const url_link = $(this).data("url");
	console.log(url_link);
	const project_list = [];
	const projectID = $(".project-checkbox");
	for (let i = 0; i < projectID.length; i++) {
		if (projectID.is(":checked")) {
			project_list.push(projectID[i].value);
		}
	}
	console.log(project_list);
	$.post({
		url: url_link,
		method: "POST",
		data: {
			projectList: JSON.stringify(project_list),
			csrfmiddlewaretoken: csrftoken,
		},
		success: (response) => {
			console.log(response);
		},
		error: (error) => {
			console.log(error);
		},
	});
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
	let currentDate = new Date();
	// Extract date components
	let day = currentDate.getDate();
	let month = currentDate.getMonth() + 1; // Month is zero-based
	let year = currentDate.getFullYear();
	// Format the date as needed (example: DD/MM/YYYY)
	let todayDate = year+'-'+month+'-'+day;
	// write the file name
	let filename = "projects_bulk_export_"+todayDate;

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
	if(fileFormat === 'xlsx'){
		fetch(export_url, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": csrftoken,
			},
			body: JSON.stringify(selected_project_list),
		}).then(response => response.json())
		.then(data => {
			// Create a link element
			const link = document.createElement('a');
			link.href = data.file_url; // Use the base64-encoded URL
			link.download = data.file_name; // Set the filename for download
			
			// Append the link to the body, click it to start download, and then remove it
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
		})
		.catch((error) => {
			console.error("Error downloading:", error);
		}).finally(()=>{
			downloadButton.setAttribute("disabled", "false");
			downloading_spinner.style.display = "none";
			icon_downloading.style.display = "inline-block";
		});
	} else if(fileFormat === 'csv'){
		fetch(export_url, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": csrftoken,
			},
			body: JSON.stringify(selected_project_list),
		}).then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename+".csv";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        })
		.catch((error) => {
			console.error("Error downloading:", error);
		}).finally(()=>{
			downloadButton.setAttribute("disabled", "false");
			downloading_spinner.style.display = "none";
			icon_downloading.style.display = "inline-block";
		});
	} else if(fileFormat === 'json'){
		fetch(export_url, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": csrftoken,
			},
			body: JSON.stringify(selected_project_list),
		}).then(response => response.blob()).then(blob =>{
			const url = window.URL.createObjectURL(blob); 
			const link = document.createElement('a'); 
			link.href = url;
			link.download = filename+'.json';
			document.body.appendChild(link); 
			link.click(); 
			document.body.removeChild(link);
			window.URL.revokeObjectURL(url); 
	
		})
		.catch((error) => {
			console.error("Error downloading:", error);
		}).finally(()=>{
			downloadButton.setAttribute("disabled", "false");
			downloading_spinner.style.display = "none";
			icon_downloading.style.display = "inline-block";
		});
	}
}
