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

stepFourApp.controller("createContractStepFourCtrl", function($scope) {
	$scope.changeEditMode = function(mode,index) {
		var getOutOfEditMode = ($scope.editMode === mode);
		
		if (getOutOfEditMode) { $scope.editMode = ""; $scope.currentlyEditing = ""; }
		else { $scope.editMode = mode; }
		
		for (var iterator = 0; iterator < $scope.editModeLabels.length; iterator++) {
			$scope.editModeLabels[iterator] = "Edit";
		}
		
		if (!getOutOfEditMode) { $scope.editModeLabels[index] = "Finish Editing"; }
	};
	$scope.changeWhatWeAreEditing = function(field) {
		$scope.currentlyEditing = field;
	};
	$scope.updatePhoneNumber = function() {
		$scope.phoneNumber = $scope.companyContactPhone1 + "-" + $scope.companyContactPhone2 + "-" + $scope.companyContactPhone3;
	};
	$scope.updateTotals = function(overrideHours) {
		var totalMilestoneProjectCost = 0;
		
		var iterator = 1;
		while ($scope["milestoneTotal" + iterator]) {
			if (overrideHours) {
				$scope["milestoneTotal" + iterator] = ($scope["estimateHourCompletion" + iterator] * $scope.hourlyRate);
			}
			totalMilestoneProjectCost = totalMilestoneProjectCost + $scope["milestoneTotal" + iterator];
			iterator++;
		}
		
		$scope.totalMilestoneProjectCost = totalMilestoneProjectCost;
	};
});

stepFiveApp.controller("createContractStepFiveCtrl", function($scope) {
	$scope.changeEditMode = function() {
		var getOutOfEditMode = ($scope.primaryEditLabel === "Finish Editing");
		
		if (getOutOfEditMode) {
			$scope.primaryEditLabel = "Edit";
			$scope.mode = "";
		}
		else {
			$scope.primaryEditLabel = "Finish Editing";
			$scope.mode = "edit";
		}
	};
});