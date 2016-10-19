'use strict';
var path = window.location.pathname;
//alert(path);
var a = path.split("/");
var i = a.pop();
//alert(i);
//alert("OK");

/*$log.log($location.path());
$log.log("OK"); */
var flcollApp = angular.module('flcollApp', ['ngRoute', 'ui.bootstrap', 'flform', 'suivi', 'newevt']);

flcollApp.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
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
        $scope.popup1 = { opened: false };
        $scope.popup2 = { opened: false };
        $scope.popup3 = { opened: false };
        $scope.popup4 = { opened: false };
        /* $scope.today = function() {
            $scope.dt = new Date();
        };
        $scope.today(); */
        $scope.dateOptions = {
            /* dateDisabled: disabled,
            formatYear: 'yy', */
            minDate: new Date(),
            maxDate: new Date(2020, 5, 22)
            /* startingDay: 1 */ /* vérifier que la $locale est utilisée */
        };
        $scope.dateOptionsDateFin = {
            minDate: $scope.evenement.date,
            maxDate: new Date(2020, 5, 22)
        };
        $scope.dateOptionsOuvInsc = {
            minDate: new Date(),
            maxDate: $scope.evenement.date
        };
        $scope.dateOptionsClotInsc = {
            minDate: $scope.evenement.date_ouverture_inscriptions,
            maxDate: $scope.evenement.date_fin ? $scope.evenement.date_fin : $scope.evenement.date
        };
        $scope.formats = ['dd-MMMM-yyyy', 'dd/MM/yyyy', 'shortDate'];
        $scope.format = $scope.formats[1];
        $log.log($scope.format);
        $scope.altInputFormats = ['dd/MM/yyyy'];
        $scope.open1 = function() {
            $scope.popup1.opened = true;
        };
        $scope.open2 = function() {
            $scope.popup2.opened = true;
        };
        $scope.open3 = function() {
            $scope.dateOptionsOuvInsc.maxDate = $scope.evenement.date;
            $scope.popup3.opened = true;
        };
        $scope.open4 = function() {
            $scope.dateOptionsClotInsc.minDate = $scope.evenement.date_ouverture_inscriptions;
            $scope.dateOptionsClotInsc.maxDate = $scope.evenement.date_fin ? $scope.evenement.date_fin : $scope.evenement.date;
            $scope.popup4.opened = true;
        };
        $log.log("tout lu");
    }]);

var suivi = angular.module('suivi',[])
.controller('suiviCtrl', ['$scope', '$log', '$http', function ($scope, $log, $http) {
    $log.log("in suivi");
}]);

var flform = angular.module('flform',['ngRoute'])
    .config(['$locationProvider',
             function($locationProvider) {
                 $locationProvider.html5Mode({
                     enabled: true,
                     requireBase: false
                 });
             }])
    .controller('flformCtrl', ['$scope', '$log', '$http', '$location', '$route', '$routeParams', function ($scope, $log, $http, $location) {
        $log.log("in flform");
        $log.log($location.path());
        $http.get('/api/evenement/1').then(function(resp) {
            console.log(resp.data);
        });
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
