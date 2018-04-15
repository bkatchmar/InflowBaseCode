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
	$scope.addMilestone = function() {
		var totalNumberOfMilestones = $scope.milestones.length+$scope.current_milestone_count+1;
		$scope.milestones.push({"index":totalNumberOfMilestones, "estimateHourCompletion" : 0, "totalMilestoneAmount" : 0.00});
	};
	$scope.updateTotals = function(overrideHours) {
		var calculatedTotalAmount = 0.00;
		
		// Get the milestones that were previously loaded in
		for (var iterator = 0; iterator < $scope.current_milestone_count; iterator++) {
			if ($scope.estimateHourCompletion[iterator] > 0 && !overrideHours) {
				$scope.totalMilestoneAmount[iterator] = $scope.estimateHourCompletion[iterator] * $scope.hourlyRate;
			}
			if (overrideHours) {
				$scope.estimateHourCompletion[iterator] = 0;
			}
			calculatedTotalAmount = calculatedTotalAmount + $scope.totalMilestoneAmount[iterator];
		}
		
		// Get the recently added milestones
		for (var iterator = 0; iterator < $scope.milestones.length; iterator++) {
			if ($scope.milestones[iterator].estimateHourCompletion > 0) {
				$scope.milestones[iterator].totalMilestoneAmount = $scope.milestones[iterator].estimateHourCompletion * $scope.hourlyRate;
			}
			
			calculatedTotalAmount = calculatedTotalAmount + $scope.milestones[iterator].totalMilestoneAmount;
		}
		$scope.contractTotal = calculatedTotalAmount;
		$scope.changeRate($scope.downPaymentRate);
	};
	$scope.changeRate = function(rate) {
		$scope.downPaymentRate = rate;
		$scope.downPaymentAmount = $scope.contractTotal * rate;
	};
});