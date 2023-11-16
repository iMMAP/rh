import Swal from 'sweetalert2'

export default function initSWPopup() {

    function showConfirmModal(event) {
      	// Prevent the default behavior of the click event
      	event.preventDefault();
      	event.stopPropagation();

      	// Get the relevant data attributes from the clicked element
		var dataURL = event.currentTarget.dataset.url;
		var returnURL = event.currentTarget.dataset.returnUrl;
		var name = event.currentTarget.dataset.recordName;
		var popupType = event.currentTarget.dataset.type;

      	// Initialize variables to be used in the SweetAlert2 modal
		var title, text, icon, dangerMode, successMessage;

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
			text =
			"Unarchiving the selected record will be reactivate in draft state.";
			icon = "warning";
			dangerMode = true;
			successMessage = `Done! ${name} has been unarchived successfully!`;
		}

		// Display the SweetAlert2 modal with the appropriate variables
		Swal.fire({
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
					success: function (data) {
					// If the AJAX request is successful, display a success message and redirect
					if (data.success) {
						Swal.fire(successMessage, {
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
				error: function (error_data) {
					// If the AJAX request fails, display an error message
					Swal.fire(`Something went wrong! ${error_data}`);
					},
				});
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
	$(".show_sw_popup").on("click", function(event) {
		showConfirmModal(event)
	});

	$(".show-sw-confirm-button").on("click", function(event) {
		showConfirmationPopup(event)
	});
}
