'use strict';
var flcollApp = angular.module('flcollApp', ['flform', 'suivi', 'newevt']);

flcollApp.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);

var flform = angular.module('flform',[])
    .controller('flformCtrl', ['$scope', '$log', '$http', function ($scope, $log, $http) {
        $log.log("in flform");
        $scope.master = {};
        $scope.update = function(personne) {
            $log.log("in update");
            $scope.master = angular.copy(personne);
        };
        $scope.reset = function(form) {
            $log.log("in reset");
            if (form) {
                form.$setPristine();
                form.$setUntouched();
            }
            $scope.personne = angular.copy($scope.master);
        };
        $scope.reset();
    }]);

var newevt = angular.module('newevt',['ui.bootstrap'])
    .controller('newevtCtrl', ['$scope', '$log', '$http', function ($scope, $log, $http) {
        $log.log("in newevt");
        $scope.master = {};
        $scope.update = function(evenement) {
            $log.log("in update");
            $scope.master = angular.copy(evenement);
        };
        $scope.reset = function(form) {
            $log.log("in reset");
            if (form) {
                form.$setPristine();
                form.$setUntouched();
            }
            $scope.evenement = angular.copy($scope.master);
        };
        $scope.reset();
    }]);

var suivi = angular.module('suivi',[])
.controller('suiviCtrl', ['$scope', '$log', '$http', function ($scope, $log, $http) {
    $log.log("in suivi");
}]);
