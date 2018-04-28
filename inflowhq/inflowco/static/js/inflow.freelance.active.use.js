Dropzone.options.inflowDropzone = {
	paramName: "freelancer-deliverables", // The name that will be used to transfer the file
	clickable: true,
	addRemoveLinks: true,
	autoProcessQueue : false,
	accept: function(file, done) {
		done();
		myDropzone = this;
		myDropzone.processQueue();
		jQuery("main div.upload-modal form").submit();
	},
	init : function() {
		var submitButton = document.querySelector("#dropzone-uploader");
		myDropzone = this;
	}
};
Dropzone.prototype.defaultOptions.dictDefaultMessage = "Drag Your Files Here To Upload";
Dropzone.prototype.defaultOptions.dictFallbackText = "You are using a much older browser, using a standard HTML file input";

/* Gooogle Drive API */
//The Browser API key obtained from the Google API Console.
var developerKey = "AIzaSyAe7oJuNMKgBpReacIm04QQc_gtqJDV_xc";

// The Client ID obtained from the Google API Console. Replace with your own Client ID.
var clientId = "664505544030-uba2jj5ipgovhctdruc06m6vt8ojp3ml.apps.googleusercontent.com";

var appId = "664505544030";

// Scope to use to access user's drive files.
var scope = "https://www.googleapis.com/auth/drive";

var pickerApiLoaded = false;
var oauthToken;

// Use the API Loader script to load google.picker and gapi.auth.
function onApiLoad() {
	gapi.load("auth2", onAuthApiLoad);
	gapi.load("picker", onPickerApiLoad);
}

function onAuthApiLoad() {
	var authBtn = document.getElementById('google-drive-authorization');
    authBtn.disabled = false;
    authBtn.addEventListener('click', function() {
		gapi.auth2.authorize({
			client_id: clientId,
			scope: scope
		}, handleAuthResult);
	});
}

function onPickerApiLoad() {
	pickerApiLoaded = true;
    createPicker();
}

function handleAuthResult(authResult) {
	if (authResult && !authResult.error) {
		oauthToken = authResult.access_token;
		createPicker();
	}
}

// Create and render a Picker object for searching images.
function createPicker() {
	if (pickerApiLoaded && oauthToken) {
		var view = new google.picker.View(google.picker.ViewId.DOCS);
		view.setMimeTypes("image/png,image/jpeg,image/jpg");
		var picker = new google.picker.PickerBuilder()
			.enableFeature(google.picker.Feature.NAV_HIDDEN)
			.enableFeature(google.picker.Feature.MULTISELECT_ENABLED)
			.setAppId(appId)
			.setOAuthToken(oauthToken)
			.addView(view)
			.addView(new google.picker.DocsUploadView())
			.setDeveloperKey(developerKey)
			.setCallback(pickerCallback)
			.build();
		picker.setVisible(true);
	}
}

// A simple callback implementation.
function pickerCallback(data) {
	if (data.action == google.picker.Action.PICKED) {
		var fileId = data.docs[0].id;
		var dataObject = {
			"url" : "https://drive.google.com/uc?export=view&id=" + fileId,
			"embedUrl" : data.docs[0].embedUrl,
			"driveUrl" : data.docs[0].url,
			"id" : data.docs[0].id,
			"type" : data.docs[0].type,
			"mimeType" : data.docs[0].mimeType,
			"name" : data.docs[0].name
		};
		
		jQuery("main div.upload-modal form input[type='hidden'][name='drive-url']").val(dataObject["url"]);
		jQuery("main div.upload-modal form input[type='hidden'][name='drive-name']").val(dataObject["name"]);
		jQuery("main div.upload-modal form").submit();
	}
}

jQuery(document).ready(function() {
	jQuery("main div.content div.milestone-detail-list div.milestone-name-upload span.upload a").leanModal({ closeButton: ".modal-cancel" });
	jQuery("main div.upload-modal form input[type='file']").change(function() {
		jQuery("main div.upload-modal form").submit();
	});
});