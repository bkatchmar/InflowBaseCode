stepOneApp.controller("createContractStepOneCtrl", function($scope) {
	if (addresses.length === 0) {
		addresses.push({"index":1,"addr1":"","addr2":"","city":"","state":""});
	}
	
	$scope.contact_addresses = addresses;
	
	$scope.addAddress = function() {
		var totalNumberOfAddresses = $scope.contact_addresses.length;
		totalNumberOfAddresses = totalNumberOfAddresses + 1;
		$scope.contact_addresses.push({"index":totalNumberOfAddresses,"addr1":"","addr2":"","city":"","state":""});
	};
});

stepTwoApp.controller("createContractStepTwoCtrl", function($scope) {
	if (milestones.length === 0) {
		milestones.push({"index":1, "name" : "", "description" : "", "estimateHourCompletion" : 0, "totalMilestoneAmount" : 0.00, "milestoneDeadline" : ""});
	}
	
	$scope.milestones = milestones;
	$scope.addMilestone = function() {
		var totalNumberOfMilestones = $scope.milestones.length;
		totalNumberOfMilestones = totalNumberOfMilestones + 1;
		$scope.milestones.push({"index":totalNumberOfMilestones, "name" : "", "description" : "", "estimateHourCompletion" : 0, "totalMilestoneAmount" : 0.00, "milestoneDeadline" : ""});
	};
	$scope.updateTotals = function() {
		console.log("Look");
	};
});