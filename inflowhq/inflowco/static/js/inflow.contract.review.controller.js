reviewApp.controller("contractReviewCtrl", function($scope) {
	$scope.initArrayVals = function() {
        $scope.editLabels = ["Edit"];
        $scope.editObjects = [];
    };
    $scope.changeLabels = function(index) {
        // Change the label
        if ($scope.editLabels[index] === "Edit") {
            $scope.editLabels[index] = "Finish Editing";
        } else {
            $scope.editLabels[index] = "Edit";
            $scope.editMode = "";
            $scope.whatWeAreEditing = "";
        }
    };
    $scope.changeMode = function(mode) {
        if ($scope.editMode === mode) {
            $scope.editMode = "";
            $scope.whatWeAreEditing = "";
        } else {
            $scope.editMode = mode;
        }
    };
    $scope.changeWhatEditing = function(what) {
        if ($scope.whatWeAreEditing === what) {
            $scope.whatWeAreEditing = "";
        } else {
            $scope.whatWeAreEditing = what;
        }
    };
    $scope.cancelEdit = function() {
        $scope.whatWeAreEditing = "";
    };
    $scope.doesTheCurrentEditObjectsContainElement = function(field) {
        return false;
    };
});