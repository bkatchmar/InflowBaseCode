stepOneApp.controller("createContractStepOneCtrl", function($scope) {});

stepTwoApp.controller("createContractStepTwoCtrl", function($scope, $http) {
	$scope.loadInMilestones = function() {
		$scope.milestones=[];
		$scope.toDelete = 0;
		
		$http.get("/inflow/projects/contract-service/milestones/" + $scope.contractId).then(function(response) {
			if (response.data["success"] && response.data["milestones"]) {
				$scope.milestones=response.data["milestones"];
			}
			
			if ($scope.milestones.length === 0) {
				$scope.addMilestone();
			}
		});
	};
	$scope.addMilestone = function() {
		var totalNumberOfMilestones = $scope.milestones.length+1;
		$scope.milestones.push({"index":totalNumberOfMilestones, "id" : 0, "name" : "", "description": "", "payment_amount" : 0, "deadline" : "", "estimate_hours_required" : 0});
	};
	$scope.updateTotals = function(overrideHours) {
		var calculatedTotalAmount = 0.00;
		
		// Get the milestones that were previously loaded in
		for (var iterator = 0; iterator < $scope.milestones.length; iterator++) {
			if ($scope.milestones[iterator].estimate_hours_required > 0 && !overrideHours) {
				$scope.milestones[iterator].payment_amount = $scope.milestones[iterator].estimate_hours_required * $scope.hourlyRate;
			}
			if (overrideHours) {
				$scope.milestones[iterator].estimate_hours_required = 0;
			}
			calculatedTotalAmount = calculatedTotalAmount + $scope.milestones[iterator].payment_amount;
		}
		
		$scope.contractTotal = calculatedTotalAmount;
	};
	$scope.generateDatePickersForUnusedDateFields = function() {
		jQuery("div.input-field.date input[type='text']:not(.hasDatepicker)").datepicker({showOtherMonths:true,selectOtherMonths:true,dateFormat:"M dd yy"});
	};
});

stepThreeApp.controller("createContractStepThreeCtrl", function($scope) {});

stepFourApp.controller("createContractStepFourCtrl", function($scope) {});

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
		$scope.currentlyEdit = "";
	};
	$scope.changeCurrentEdit = function(mode) {
		$scope.currentlyEdit = mode;
	};
});