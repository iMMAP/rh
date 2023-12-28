/**
* Ready Function
**/
$(function () {

	$(".js_multiselect").select2();

	$('tr[data-url]').on('click', function() {
		window.location.href = $(this).data('url');
	});
});