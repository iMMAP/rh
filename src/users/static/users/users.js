$(function () {
	$('.js_multiselect').select2();
	$(".show-password").text("Show password");
	$('.show-password').on('click', function(){
		
			$(this).text(function(){
			  if($(this).text() === 'Show password'){
				$('#id_password').attr('type','text');
				return 'Hide password';
			} else {
				$('#id_password').attr('type','password');
				return 'Show password';
			}
		  });
	});
});
