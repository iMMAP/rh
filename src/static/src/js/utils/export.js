
export default function initExport() {
  $(".export-button").on('click', function(event) {
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
}
