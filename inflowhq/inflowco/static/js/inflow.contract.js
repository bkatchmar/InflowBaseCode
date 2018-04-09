jQuery(document).ready(function() {
	var textAreaSelector = "main div.create-contract-super-window form.contract-creation div.input-field span.field textarea";
	var textAreaCounter = "main div.create-contract-super-window form.contract-creation div.input-field.text-multi-line div.counter span.count";
	
	jQuery(textAreaSelector).keydown(function() {
		var totalLength = jQuery(textAreaSelector).val().length;
		jQuery(textAreaCounter).text(totalLength);
	});
});