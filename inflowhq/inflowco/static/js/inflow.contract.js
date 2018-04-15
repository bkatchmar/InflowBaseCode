jQuery(document).ready(function() {
	var textAreaSelector = "main div.create-contract-super-window form.contract-creation div.input-field span.field textarea";
	var textAreaCounter = "main div.create-contract-super-window form.contract-creation div.input-field.text-multi-line div.counter span.count";
	var calculateTotalAndRemaining = function() {
		if (jQuery(textAreaSelector).val()) {
			var totalLength = jQuery(textAreaSelector).val().length;
			jQuery(textAreaCounter).text(totalLength);	
		}
	};
	
	calculateTotalAndRemaining();
	jQuery(textAreaSelector).keydown(function() {
		calculateTotalAndRemaining();
	});
	
	jQuery("div.input-field.date input[type='text']").datepicker({showOtherMonths:true,selectOtherMonths:true,dateFormat:"M dd yy"});
});

function generateDatePickersForUnusedDateFields() {
	jQuery("div.input-field.date input[type='text']:not(.hasDatepicker)").datepicker({showOtherMonths:true,selectOtherMonths:true,dateFormat:"M dd yy"});
}