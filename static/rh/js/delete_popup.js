import swal from 'sweetalert';

$(function () {
    $('.show_confirm').click(function (event) {
        debugger
        var deleteURL = $("#delete-project").attr("data-url");;
        var returnURL = $("#return-url").attr("href");;
        var name = $('#project-code').text()
        event.preventDefault();
        swal({
            title: `Are you sure you want to delete ${name}?`,
            text: "Once deleted, you will not be able to recover this project!",
            icon: "warning",
            buttons: true,
            dangerMode: true,
        })
            .then((willDelete) => {
                if (willDelete) {
                    $.ajax({
                        method: 'GET',
                        url: deleteURL,
                        success: function (data) {
                            debugger
                            if (data.success) {
                                debugger
                                swal(`Done! Your Project ${name} has been deleted!`, {
                                    icon: "success",
                                }).then(() => {
                                    window.location.href = returnURL
                                })
                            }
                        },
                        error: function (error_data) {
                            swal(`Something went wrong! ${error_data}`);
                        }
                    })
                } else {
                    swal("Your project is safe!");
                }
            });
    });
})