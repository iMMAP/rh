/**
* Ready Function
**/
$(function () {

    $('tr[data-url]').on('click', function(e) {
        const url = $(this).data('url');
        window.location.href = url;
	});
    
});