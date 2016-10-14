'use strict';
var flcollApp = angular.module('flcollApp', ['flform']);
var flform = angular.module('flform',[]);

flcollApp.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);

flform.controller('flformCtrl', ['$scope', function ($scope) {
    $scope.master = {};
    $scope.update = function(personne) {
        $scope.master = angular.copy(personne);
    };
    $scope.reset = function() {
        $scope.personne = angular.copy($scope.master);
    };
    $scope.reset();
}]);
