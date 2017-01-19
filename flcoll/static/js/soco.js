'use strict';
var socoApp = angular.module('socoApp', ['ngRoute', 'suivi', 'newevt']);

socoApp.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);

function listProperties(obj) {
    var propList = "";
    for(var propName in obj) {
        if(typeof(obj[propName]) != "undefined") {
            propList += (propName + ", ");
        }
    }
    return propList;
}
var findProperties = function(obj) {
    var aPropertiesAndMethods = [];
    do {
        aPropertiesAndMethods = aPropertiesAndMethods.concat(Object.getOwnPropertyNames(obj));
    } while (obj = Object.getPrototypeOf(obj));
    for ( var a = 0; a < aPropertiesAndMethods.length; ++a) {
        for ( var b = a + 1; b < aPropertiesAndMethods.length; ++b) {
            if (aPropertiesAndMethods[a] === aPropertiesAndMethods[b]) {
                aPropertiesAndMethods.splice(a--, 1);
            }
        }
    }
    return aPropertiesAndMethods;
}

function reload(){ // FIXME
    var container = document.getElementById("datefin");
    var content = container.innerHTML;
    container.innerHTML= content;
}

var suivi = angular.module('suivi',[])
.controller('suiviCtrl', ['$scope', '$log', '$http', function ($scope, $log, $http) {
    $log.log("in suivi");
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
        ncollform.date_fin.minDate=$scope.evenement.date;
        var $minDate = $scope.evenement.date;
        $log.log("$minDate = " + $minDate);
        //ncollform.date_cloture_inscriptions.maxDate=$scope.evenement.date;
        $log.log("min=" + ncollform.date_fin.min);
        ncollform.date_fin.min = $minDate;
        $log.log("min=" + ncollform.date_fin.min);
        ncollform.date_fin.selectionStart = $minDate;
        var $cont = document.getElementById("datefin");
        var $inp = $cont.innerHTML;
        $log.log($inp); // introspection
        //ncollform.date_fin.focus();
        //$log.log(listProperties(ncollform.date_fin));
        //$log.log("ok");
        };
    $scope.calc2 = function() {
        $log.log("in calc2");
        $log.log("min = " + ncollform.date_fin.min);
        $log.log("date_fin = " + $scope.evenement.date_fin);
        $log.log("ok ?" + ($scope.evenement.date_fin >= ncollform.date_fin.min));
        if ($scope.evenement.date_fin < $scope.evenement.date) {
            alert("la date de fin ne peut pas être antérieure à la date de l'événement !");
            $scope.evenement.date_fin = $scope.evenement.date;
        }
        ncollform.date_cloture_inscriptions.maxDate=$scope.evenement.date_fin;
        };
    $scope.calc3 = function() {
        $log.log("in calc3");
        $log.log("date_ouverture_inscriptions = " + $scope.evenement.date_ouverture_inscriptions);
        ncollform.date_cloture_inscriptions.minDate=$scope.evenement.date_ouverture_inscriptions;
        };
        $log.log("tout lu");
}]);
