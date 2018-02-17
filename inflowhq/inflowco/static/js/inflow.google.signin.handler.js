function InflowRenderGoogleButton() {
	gapi.signin2.render("google-signin", {
		"scope": "profile email",
 		"width": 193,
 		"height": 36,
 		"longtitle": true,
 		"theme": "dark",
 		"onsuccess": InflowGoogleSignIn,
 		"onfailure": onFailure
	});
}

function InflowGoogleSignIn(googleUser) {
	var google_id_token = googleUser.getAuthResponse().id_token;
 	
	// Fill in the form
 	jQuery("form.login-form input[type='hidden'][name='google-id-token']").val(google_id_token);
 	jQuery("form.login-form").submit();
}
function onFailure(error) {}