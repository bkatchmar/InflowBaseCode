stepOneApp.controller("createContractStepOneCtrl", function($scope) {
	if (addresses.length === 0) {
		addresses.push({"index":1,"addr1":"","addr2":"","city":"","state":""});
	}
	
	$scope.contact_addresses = addresses;
	
	$scope.addAddress = function() {
		var totalNumberOfAddresses = $scope.contact_addresses.length;
		totalNumberOfAddresses = totalNumberOfAddresses + 1;
		$scope.contact_addresses.push({"index":totalNumberOfAddresses,"addr1":"","addr2":"","city":"","state":""});
	}
});