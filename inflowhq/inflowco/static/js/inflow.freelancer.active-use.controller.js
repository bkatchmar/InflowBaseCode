milestonesApp.controller("milestonesCtrl", function($scope, $http) {
	$scope.deleteMilestoneFile = function(id,milestoneId) {
		$scope.deletedFiles[milestoneId].push(id);
		$http.get("/inflow/projects/contract-service/delete-milestone-file/" + id).then(function(response) {});
	};
});