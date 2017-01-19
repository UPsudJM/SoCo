'use strict';
var socoApp = angular.module('socoApp', ['ngRoute', 'suivi', 'newevt']);

socoApp.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);

var suivi = angular.module('suivi',[])
.controller('suiviCtrl', ['$scope', '$log', '$http', function ($scope, $log, $http) {
    $log.log("in suivi");
}]);

var newevt = angular.module('newevt',['pickadate'])
.config(function(pickadateI18nProvider) {
    pickadateI18nProvider.translations = {
        prev: '<em>&lt;&lt; prec</em>',
        next: '<em>suiv &gt;&gt;</em>',
        varDelimStart: '[[',
        varDelimEnd: ']]'
    }
})
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
        $scope.today = function() {
            $scope.dt = new Date();
        };
        $scope.today();
    $scope.calc1 = function() {
        $log.log("in calc1");
        $log.log("date = " + $scope.evenement.date);
        ncollform.date_fin.minDate=$scope.evenement.date;
        ncollform.date_cloture_inscriptions.maxDate=$scope.evenement.date;
        };
    $scope.calc2 = function() {
        $log.log("in calc2");
        $log.log("date_fin = " + $scope.evenement.date_fin);
        ncollform.date_cloture_inscriptions.maxDate=$scope.evenement.date_fin;
        };
    $scope.calc3 = function() {
        $log.log("in calc3");
        $log.log("date_ouverture_inscriptions = " + $scope.evenement.date_ouverture_inscriptions);
        ncollform.date_cloture_inscriptions.minDate=$scope.evenement.date_ouverture_inscriptions;
        };
        $log.log("tout lu");
}]);
