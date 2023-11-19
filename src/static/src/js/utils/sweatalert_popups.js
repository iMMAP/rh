import Swal from 'sweetalert2'

export default function initSWPopup() {

    function showActionConfirmPopup(event) {
      	// Prevent the default behavior of the click event
      	event.preventDefault();
      	event.stopPropagation();

      	// Get the relevant data attributes from the clicked element
		var dataURL = event.currentTarget.dataset.url;
		var name = event.currentTarget.dataset.name;
		var popupType = event.currentTarget.dataset.type;

      	// Initialize variables to be used in the SweetAlert2 modal
		var title, text, icon, successMessage, confirmButtonText;

		// Set the modal variables based on the type of popup requested
		if (popupType === "copy") {
			title = `Are you sure you want to duplicate ${name}?`;
			text = "";
			icon = "warning";
			confirmButtonText = 'Yes, duplicate it'
			successMessage = `Done! ${name} has been duplicated successfully!`;
		} else if (popupType === "delete") {
			title = `Are you sure you want to delete this ${name}?`;
			text = "Once deleted, you will not be able to recover this record!";
			icon = "warning";
			confirmButtonText = 'Yes, delete it'
			successMessage = `Done! ${name} has been deleted successfully!`;
		} else if (popupType === "archive") {
			title = `Are you sure you want to archive ${name}?`;
			text =
			"Archiving the selected record will deactivate it and make it unavailable to users. Please contact the administrator if you need to access the archived records in the future!";
			icon = "warning";
			confirmButtonText = 'Yes, archive it'
			successMessage = `Done! ${name} has been archived successfully!`;
		} else if (popupType === "unarchive") {
			title = `Are you sure you want to unarchive ${name}?`;
			text =
			"Unarchiving the selected record will be reactivate in Draft/Todo state.";
			icon = "warning";
			confirmButtonText = 'Yes, unarchive it'
			successMessage = `Done! ${name} has been unarchived successfully!`;
		}

		

		Swal.fire({
			title: title,
			text: text,
			icon: icon,
			showCancelButton: true,
			confirmButtonColor: "#3085d6",
			cancelButtonColor: "#d33",
			confirmButtonText: confirmButtonText,
			customClass: {
				confirmButton: 'btn btn-red',
				cancelButton: 'btn btn-danger',
				loader: 'custom-loader',
			},
			preConfirm: async (message) => {
				try {
					const response = await $.ajax({
						method: "GET",
						url: dataURL,
						data: {'message': message},
						success: function (data) {
							return data
						},
						error: function (error) {
							Swal.showValidationMessage(`
								Request failed: ${error}
							`);
						},
					});
					return response
				} catch (error) {
					Swal.showValidationMessage(`
						Request failed: ${error}
					`);
			  	}
			},
			allowOutsideClick: () => !Swal.isLoading()
		}).then((result) => {
			if (result.isConfirmed) {
				// Show success notification first
				Swal.fire({
					position: "top-end",
					icon: "success",
					title: successMessage,
					showConfirmButton: false,
					timer: 1500
				});
	
				// Delay the page reload to allow the notification to be shown
				setTimeout(() => {
					window.location.href = result.value.redirect_url;
				}, 1500); // Adjust the delay time as needed
			}
		});
	}

	function showConfirmationPopup(event) {
		event.preventDefault();
		event.stopPropagation();
		// Get the relevant data attributes from the clicked element
		var dataURL = event.currentTarget.dataset.url;
		var dataButtonText = event.currentTarget.dataset.button;
		var message = ''
		var textInput = false
		var title = ''
		if (dataButtonText == 'Reject Report'){
			message = 'Report has been rejected!'
			title = 'Please provide a short rejection reason?'
			textInput = 'text'
		}
		if (dataButtonText == 'Submit Report'){
			message = 'Report has been submitted!'
			title = 'Are you sure you want to submit report?'
		}
		if (dataButtonText == 'Approve Report'){
			message = 'Report has been approved!'
			title = 'Are you sure you want to approve report?'
		}
		Swal.fire({
			title: title,
			input: textInput,
			inputAttributes: {
			  autocapitalize: "off"
			},
			showCancelButton: true,
			confirmButtonText: dataButtonText,
			showLoaderOnConfirm: true,
			customClass: {
				input: 'sw-input-width',
				confirmButton: 'btn btn-red',
				cancelButton: 'btn btn-danger',
				loader: 'custom-loader',
			},
			preConfirm: async (message) => {
				try {
					const response = await $.ajax({
						method: "GET",
						url: dataURL,
						data: {'message': message},
						success: function (data) {
							return data
						},
						error: function (error) {
							Swal.showValidationMessage(`
								Request failed: ${error}
							`);
						},
					});
					return response
				} catch (error) {
					Swal.showValidationMessage(`
						Request failed: ${error}
					`);
			  	}
			},
			allowOutsideClick: () => !Swal.isLoading()
		}).then((result) => {
			if (result.isConfirmed) {
				// Show success notification first
				Swal.fire({
					position: "top-end",
					icon: "success",
					title: message,
					showConfirmButton: false,
					timer: 1500
				});
	
				// Delay the page reload to allow the notification to be shown
				setTimeout(() => {
					window.location.href = result.value.redirect_url;
				}, 1500); // Adjust the delay time as needed
			}
		});
	}

	// Attach the click event listener to all elements with class "show_confirm"
	$(".show-sw-action-popup").on("click", function(event) {
		showActionConfirmPopup(event)
	});

	$(".show-sw-confirm-button").on("click", function(event) {
		showConfirmationPopup(event)
	});
}
