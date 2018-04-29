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