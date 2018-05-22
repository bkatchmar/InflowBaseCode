if (typeof gapi !== 'undefined') {
	if (gapi.auth2 == undefined) {
		gapi.load("auth2", function() {
			auth2 = gapi.auth2.init({
				client_id: "857316650586-gm54140nh8ifnvls7s8acbntv3cp915e.apps.googleusercontent.com",
			    fetch_basic_profile: false,
			    scope: "profile email"
			});
		});
	}
}

function InflowGoogleSignOut() {
	var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut();
}

jQuery(document).ready(function() {
	jQuery("main div.content div.ribbon span.non-button a").click(function(event) {
		InflowGoogleSignOut();
	});
	jQuery("main h1.error a").click(function(event) {
		InflowGoogleSignOut();
	});
});