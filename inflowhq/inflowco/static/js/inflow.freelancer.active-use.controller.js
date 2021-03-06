milestonesApp.controller("milestonesCtrl", function($scope, $http) {
	$scope.deleteMilestoneFile = function(id,milestoneId) {
		$scope.deletedFiles[milestoneId].push(id);
		$http.get("/inflow/projects/contract-service/delete-milestone-file/" + id).then(function(response) {});
	};
});

filesApp.controller("filesCtrl", function($scope, $http) {
	$scope.deleteContractFile = function(id) {
		$scope.deletedFiles.push(id);
		$http.get("/inflow/projects/contract-service/delete-contract-file/" + id).then(function(response) {});
	};
});

contactsAccordianApp.controller("contactsAccordianCtrl", function($scope) {});

contractOverviewApp.controller("contractOverviewCtrl", function($scope) {
	$scope.changeEditMode = function() {
		if ($scope.editMode==0) {
			$scope.editMode=1;
			$scope.editModeText="Finished Editing";
		} else {
			$scope.editMode=0;
			$scope.editModeText="Edit information";
		}
	};
	
	$scope.updatePhoneNumber = function() {
		if ($scope.billing_phone1.length === 3 && $scope.billing_phone2.length === 3 && $scope.billing_phone3.length === 4) {
			$scope.billing_phone = $scope.billing_phone1 + "-" + $scope.billing_phone2 + "-" + $scope.billing_phone3;
		} else {
			$scope.billing_phone = "";
		}
	};
});

milestoneScheduleApp.controller("milestoneScheduleCtrl", function($scope, $http) {
	$scope.updateScheduledDeliveryDate = function() {
		var selectedDeliveryDate = jQuery("main div.content div.schedule-delivery div.calendar").datepicker("getDate");
		var csrfToken = jQuery("form#schedule-delivery-token input[name='csrfmiddlewaretoken']").val();
		$http.post(
				"/inflow/projects/contract-service/schedule-milestone/" + $scope.milestoneId, 
				{"delivery":selectedDeliveryDate}, 
				{headers:{"Content-Type":"application/json","X-CSRFToken":csrfToken}})
		.then(function(response) {
			var redirectUrl = "/inflow/projects/my-contract/" + $scope.contractSlug + "-" + $scope.contractId + "/milestones/confirm-schedule/" + $scope.milestoneId;
			window.location=redirectUrl;
		});
	};
});