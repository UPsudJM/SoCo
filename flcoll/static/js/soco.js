'use strict';
var socoApp = angular.module('socoApp', ['ngRoute', 'suivi', 'newevt']);

socoApp.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);

var suivi = angular.module('suivi',['pickadate'])
    .config(function(pickadateI18nProvider) {
        pickadateI18nProvider.translations = {
            prev: '<em>&lt;&lt;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</em>',
            next: '<em>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&gt;&gt;</em>',
            varDelimStart: '[[',
            varDelimEnd: ']]'
        }
    })
    .controller('suiviCtrl', ['$scope', '$log', '$http', function ($scope, $log, $http) {
        $log.log("in suivi");
        $scope.master = {};
        $scope.auj = new Date();
        $scope.update = function(evenements) {
            $log.log("in update");
            $scope.master = angular.copy(evenements);
        };
    }]);

var newevt = angular.module('newevt',['pickadate'])
.config(function(pickadateI18nProvider) {
    pickadateI18nProvider.translations = {
        prev: '<em>&lt;&lt;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</em>',
        next: '<em>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&gt;&gt;</em>',
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
        //ncollform.date_fin.focus(); // FIXME timeout https://docs.angularjs.org/error/$rootScope/inprog?p0=$apply
        };
    $scope.calc2 = function() {
        $log.log("in calc2");
        $log.log("date_fin = " + $scope.evenement.date_fin);
        $log.log("ok ?" + ($scope.evenement.date_fin >= ncollform.date_fin.min));
        if ($scope.evenement.date_fin < $scope.evenement.date) {
            alert("La date de fin ne peut pas être antérieure à la date de l'événement !");
            $scope.evenement.date_fin = $scope.evenement.date;
        }
        ncollform.lieu.focus();
        };
    $scope.calc3 = function() {
        $log.log("in calc3");
        $log.log("date_ouverture_inscriptions = " + $scope.evenement.date_ouverture_inscriptions);
        if ($scope.evenement.date_ouverture_inscriptions > $scope.evenement.date) {
            alert("La date d'ouverture des inscriptions est postérieure à la date de l'évenement !");
        }
        //ncollform.date_cloture_inscriptions.focus();
        };
    $scope.calc4 = function() {
        $log.log("in calc4");
        $log.log("date_cloture_inscriptions = " + $scope.evenement.date_cloture_inscriptions);
        $log.log("ok ?" + ($scope.evenement.date_cloture_inscriptions >= $scope.evenement.date_ouverture_inscriptions));
        $log.log("ok ok ?" + ($scope.evenement.date_cloture_inscriptions <= $scope.evenement.date_fin));
        if ($scope.evenement.date_cloture_inscriptions < $scope.evenement.date_ouverture_inscriptions) {
            alert("La date de clôture ne peut pas être antérieure à la date d'ouverture !");
            $scope.evenement.date_cloture_inscriptions = $scope.evenement.date_ouverture_inscriptions;
        }
        if ($scope.evenement.date_cloture_inscriptions > $scope.evenement.date_fin) {
            alert("La date de clôture des inscriptions ne peut pas être postérieure à la date de fin de l'événement !");
            $scope.evenement.date_cloture_inscriptions = $scope.evenement.date_fin;
        }
        };
        $log.log("tout lu");
}]);
