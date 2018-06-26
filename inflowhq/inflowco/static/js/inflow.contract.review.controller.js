reviewApp.controller("contractReviewCtrl", function($scope) {
	$scope.initArrayVals = function() {
        $scope.editLabels = ["Edit"];
    };
    $scope.changeLabels = function(index) {
        // Change the label
        if ($scope.editLabels[index] === "Edit") {
            $scope.editLabels[index] = "Finish Editing";
        } else {
            $scope.editLabels[index] = "Edit";
        }
    };
    $scope.changeMode = function(mode) {
        if ($scope.editMode === mode) {
            $scope.editMode = "";
        } else {
            $scope.editMode = mode;
        }
    };
});