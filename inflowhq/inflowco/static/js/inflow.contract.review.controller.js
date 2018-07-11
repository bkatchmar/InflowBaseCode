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
        $scope.proposedChangeValue = "";
        $scope.proposedChangeReason = "";
    };
    $scope.appendEdit = function() {
        // First check if we even need to run these checks, otherwise the user clearly didn't bother putting something in
        if ($scope.entryIsValid()) {
            if ($scope.doesTheCurrentEditObjectsContainElement($scope.whatWeAreEditing)) {
                var index = $scope.whatIndexDoesTheFieldHaveInTheCollection($scope.whatWeAreEditing);
                $scope.editObjects[index]["newValue"] = $scope.proposedChangeValue;
                $scope.editObjects[index]["newValueReason"] = $scope.proposedChangeReason;
            } else {
                $scope.editObjects.push(
                    {
                        "fieldName" : $scope.whatWeAreEditing,
                        "newValue" : $scope.proposedChangeValue,
                        "newValueReason" : $scope.proposedChangeReason
                    }
                );
            }
        }
        
        $scope.cancelEdit();
    };
    $scope.doesTheCurrentEditObjectsContainElement = function(field) {
        for (var iterator = 0; iterator < $scope.editObjects.length; iterator++) {
            if ($scope.editObjects[iterator]["fieldName"] === field) {
                return true;
            }
        }

        return false;
    };
    $scope.whatIndexDoesTheFieldHaveInTheCollection = function(field) {
        for (var iterator = 0; iterator < $scope.editObjects.length; iterator++) {
            if ($scope.editObjects[iterator]["fieldName"] === field) {
                return iterator;
            }
        }

        return -1;
    };
    $scope.entryIsValid = function() {
        return $scope.proposedChangeValue != "" && $scope.proposedChangeReason != "";
    };
    $scope.getProposedNewValue = function(field){
        for (var iterator = 0; iterator < $scope.editObjects.length; iterator++) {
            if ($scope.editObjects[iterator]["fieldName"] === field) {
                return $scope.editObjects[iterator]["newValue"];
            }
        }

        return "";
    }
    $scope.getProposedDescription = function(field){
        for (var iterator = 0; iterator < $scope.editObjects.length; iterator++) {
            if ($scope.editObjects[iterator]["fieldName"] === field) {
                return $scope.editObjects[iterator]["newValueReason"];
            }
        }

        return "";
    }
});