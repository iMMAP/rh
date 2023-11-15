
export default function initExportAndSW() {
  jQuery(function () {
    $(".js_multiselect").select2();
    // changing the checkbox color when it checked
    $("input[type=checkbox]").change(function(){
      $(this).css("accent-color","#af4745");
    });

    $("tr[data-url]").click(function () {
      window.location.href = $(this).data("url");
    });

    $(".export-button").click(function (event) {
      event.preventDefault();
      event.stopPropagation();
      // Get the export URL from the button's data-url attribute
      var exportUrl = $(this).find("a").data("url");
      
      // Send an AJAX request to the export URL
      $.ajax({
        url: exportUrl,
        method: "POST",
        data: {
          csrfmiddlewaretoken: csrfToken,
        },
        success: function (response) {
          // Create a temporary download link and click it to trigger the file download
          var link = document.createElement("a");
          link.href = response.file_url;
          link.download = response.file_name;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        },
        error: function (xhr, status, error) {
          if (xhr.status === 400) {
            console.log("Error: No records selected for export");
          } else {
            console.log("Error: " + xhr.responseText);
          }
        },
      });
    });
    // filter the project field and download start
    $("#downloadFilterForm").click(function(e) {
      e.preventDefault();
      e.stopPropagation();
      const routeUrl = $(this).find("a").data("url");
      console.log(routeUrl)
      let exportData = {};
      let donorData = [];
      let clusterData = [];
      let activityDomainData = [];
      let implementingPartnerData = [];
      let programPartnerData = [];

      const checkedDonor = document.querySelectorAll(".input-check-donor");
      for(let i = 0; i < checkedDonor.length; i++){
        if(checkedDonor[i].checked == true){
          donorData.push(checkedDonor[i].value);
        }
      }
      const checkedCluster = document.querySelectorAll(".input-check-cluster");
      for(let i = 0; i < checkedCluster.length; i++){
        if(checkedCluster[i].checked == true){
          clusterData.push(checkedCluster[i].value);
        }
      }
      const checkedActivityDomainData = document.querySelectorAll(".input-check-activityDomain");
      for(let i = 0; i < checkedActivityDomainData.length; i++){
        if(checkedActivityDomainData[i].checked == true){
          activityDomainData.push(checkedActivityDomainData[i].value);
        }
      }
      const checkImplement = document.querySelectorAll(".input-check-implement");
      for(let i = 0; i < checkImplement.length; i++){
        if(checkImplement[i].checked == true ) {
        implementingPartnerData.push(checkImplement[i].value);
        }
      }
      const checkProgram = document.querySelectorAll(".input-check-program");
      for(let i = 0; i < checkProgram.length; i++) {
        if(checkProgram[i].checked == true) {
          programPartnerData.push(checkProgram[i].value);
        }
      }
      const checkedItem = document.querySelectorAll(".input-check");
      for(let i = 0; i < checkedItem.length; i++) {
        if(checkedItem[i].checked == true) {
          exportData[checkedItem[i].name] = checkedItem[i].value;
        }
      }
      if(donorData != '') {exportData['Donors']=donorData; alert("helo");}
      if(clusterData != '') {exportData['Clusters'] = clusterData;}
      if(activityDomainData != ''){exportData['Activity_domains'] = activityDomainData;}
      if(implementingPartnerData != ''){exportData['Implementing_partners'] = implementingPartnerData;}
      if(programPartnerData != ''){exportData['Program_partners'] = programPartnerData;}
      console.log(exportData);
      $.post({
        url: routeUrl,
        method: "POST",
        data:{
        "exportData":JSON.stringify(exportData),
        csrfmiddlewaretoken:csrfToken,
        },
        success: function (response){
          var link = document.createElement("a");
          link.href = response.file_url;
          link.download = response.file_name;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          console.log(response);
        },
        error: function (error){
          console.log("No Record Found");
        },
      });
    });

    //filter the project field and download 
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
            success: function (data) {
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
            error: function (error_data) {
              // If the AJAX request fails, display an error message
              swal(`Something went wrong! ${error_data}`);
            },
          });
        }
      });
    }
    // Attach the click event listener to all elements with class "show_confirm"
    $(".show_confirm").click(showConfirmModal);
  });
}
