var InflowLib = {
		ValidateAtLeastOneCharacter: function(str) { return str.length > 0; },
		ValidateBankRoutingNumber: function(str) { return /^([0-9]{9})$/.test(str); },
		ValidateSocialSecurity: function(str) { return /^([0-9]{4})$/.test(str); },
		ValidatePersonalIdNumber: function(str) { return /^([0-9]{9})$/.test(str); },
		ValidatePostalCode: function(str) { return /^([0-9]{5})$/.test(str); }
};