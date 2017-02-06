'use strict';

/*function getAttributes(obj) {
    var res = [];
    for(var m in obj) {
        if(typeof obj[m] != "function") {
            res.push(m)
        }
    }
    return res;
}

function getMethods(obj) {
    var res = [];
    for(var m in obj) {
        if(typeof obj[m] == "function") {
            res.push(m)
        }
    }
    return res;
}*/

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
        /* $log.log("in suivi"); */
        $scope.master = {};
        $scope.auj = new Date();
        $scope.update = function(evenements) {
            $log.log("in update");
            $scope.master = angular.copy(evenements);
        };
        $scope.reset = function(form) {
            if (form) {
                form.$setPristine();
                form.$setUntouched();
            }
            $scope.evenements = angular.copy($scope.master);
        };
        $scope.reset();
        $scope.showmodifdatecloture = function(id) {
            $log.log("in showmodifdatecloture");
            $log.log("id=" + id);
            var $v = "date_modif_" + id;
            $log.log('$scope.' + $v + ' = ' + '1');
            eval('$scope. ' + $v + ' = ' + '1');
        };
        $scope.modifdatecloture = function(id) {
            $log.log("in modifdatecloture");
            $log.log("id=" + id);
            var $v = "date_cloture_inscriptions_" + id;
            $log.log('v=' + $v);
            $log.log('$scope.evenements.' + $v);
            $log.log($scope.evenements.date_cloture_inscriptions_1);
            try {
                var $xx = eval('$scope.evenements.' + $v).split('/');
                $log.log('xx=' + $xx);
            } catch(e) {
                alert("erreur:" + e.name + "\nmessage:" + e.message);
            }
            var $params = {"id" : id, "datecloture" : $xx[2] + "-" + $xx[1] + "-" + $xx[0]};
            $log.log($params);
            $http.get('/api/modifformulaire', {'params': $params}).then(function(resp) {
                $log.log(resp.data);
                var $w = "maj_date_cloture_" + id;
                $log.log(typeof resp.data);
                $log.log('$scope.evenements.' + $w + '="' + resp.data + '"');
                eval('$scope.evenements.' + $w + '="' + resp.data + '"');
            });
            var $v = "date_modif_" + id;
            $log.log('$scope.' + $v + ' = ' + '0');
            eval('$scope. ' + $v + ' = ' + '0');
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
.controller('newevtCtrl', ['$scope', '$log', function ($scope, $log) {
    $log.log("in newevt");
    var calcule_date = function(s) {
        var tab = s.split(/[- //]/);
        return new Date(tab[2],tab[1],tab[0]);
    }
    $scope.master = {};
    $scope.update = function(evenement) {
        $log.log("in update");
        $scope.master = angular.copy(evenement);
    };
    $scope.reset = function() {
        $log.log("in reset");
        ncollform.reset();
        $scope.evenement = angular.copy($scope.master);
        $scope.evenement.texte_restauration_1 = ncollform.texte_restauration_1.defaultValue;
    };
    $scope.reset();
    $scope.today = function() {
        $scope.auj = new Date();
    };
    $scope.today();
    $scope.calc_date = function() {
        $log.log("in calc_date");
        /* $log.log("date = " + $scope.evenement.date); */
        //ncollform.date_fin.focus(); // FIXME timeout https://docs.angularjs.org/error/$rootScope/inprog?p0=$apply
        $scope.date = $scope.evenement.date;
    };
    $scope.calc_date_fin = function() {
        $log.log("in calc_date_fin");
        /* $log.log("date_fin = " + $scope.evenement.date_fin);
        $log.log("ok ?" + ($scope.evenement.date_fin >= ncollform.date_fin.min)); */
        if (calcule_date($scope.evenement.date_fin) < calcule_date($scope.evenement.date)) {
            alert("La date de fin ne peut pas être antérieure à la date de l'événement !");
            $scope.evenement.date_fin = $scope.evenement.date;
        }
        $scope.date_fin = $scope.evenement.date_fin;
        ncollform.lieu.focus();
    };
    $scope.calc_date_ouverture_inscriptions = function() {
        $log.log("in calc_ouverture_inscriptions");
        /* $log.log("date_ouverture_inscriptions = " + $scope.evenement.date_ouverture_inscriptions); */
        if (calcule_date($scope.evenement.date_ouverture_inscriptions) > calcule_date($scope.evenement.date)) {
            alert("La date d'ouverture des inscriptions est postérieure à la date de l'évenement !");
        }
        $scope.date_ouverture_inscriptions = $scope.evenement.date_ouverture_inscriptions;
        //ncollform.date_cloture_inscriptions.focus();
    };
    $scope.calc_date_cloture_inscriptions = function() {
        $log.log("in calc_date_cloture_inscriptions");
        if ($scope.evenement.date_ouverture_inscriptions && $scope.evenement.date_cloture_inscriptions && calcule_date($scope.evenement.date_cloture_inscriptions) < calcule_date($scope.evenement.date_ouverture_inscriptions)) {
            alert("La date de clôture ne peut pas être antérieure à la date d'ouverture !");
            $scope.evenement.date_cloture_inscriptions = $scope.evenement.date_ouverture_inscriptions;
        }
        if ($scope.evenement.date_fin && $scope.evenement.date_cloture_inscriptions && calcule_date($scope.evenement.date_cloture_inscriptions) > calcule_date($scope.evenement.date_fin)) {
            alert("La date de clôture des inscriptions ne peut pas être postérieure à la date de fin de l'événement !");
            $scope.evenement.date_cloture_inscriptions = $scope.evenement.date_fin;
        }
        $scope.date_cloture_inscriptions = $scope.evenement.date_cloture_inscriptions;
    };
    $scope.click_texte_restauration_1 = function() {
        $log.log("in click_texte_restauration_1");
<<<<<<< HEAD
<<<<<<< HEAD
        if ($scope.evenement.texte_restauration_1 == ncollform.texte_restauration_1.defaultValue) {
            $scope.evenement.texte_restauration_1 = "";
        }
    };
=======
        $scope.evenement.texte_restauration_1 = "";
    };

>>>>>>> ef6532e... Réaction dynamique d'un champ texte.
=======
        if ($scope.evenement.texte_restauration_1 == ncollform.texte_restauration_1.defaultValue) {
            $scope.evenement.texte_restauration_1 = "";
        }
    };
>>>>>>> 77acfb7... Dynamisation du champ texte_restauration_1.
    /* $log.log("tout lu"); */
}]);
