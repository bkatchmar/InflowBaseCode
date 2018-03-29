jQuery(document).ready(function() {
	changeHeaderHeight();
	jQuery(window).resize(function() { changeHeaderHeight(); });
});

function changeHeaderHeight() {
	var overallWindowHeight = jQuery("html").height();
	
	if (overallWindowHeight < 550) {
		// jQuery("header").css({"height" : "550px"});	
	} else {
		// jQuery("header").css({"height" : overallWindowHeight + "px"});
	}
}