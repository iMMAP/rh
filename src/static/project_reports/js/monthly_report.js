/**
* Ready Function
**/
$(function () {

	$('tr[data-url]').on('click', function() {
		window.location.href = $(this).data('url');
	});
});