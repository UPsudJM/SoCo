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
        $scope.definedefaultdate = function(id, d) {
            $log.log("in definedefaultdate");
            var $v = "default_date_" + id;
            $log.log('$scope.' + $v + ' = "' + d + '"');
            eval("$scope. " + $v + "= new Date('" + d + "')");
        };
        $scope.showmodifdatecloture = function(id) {
            $log.log("in showmodifdatecloture");
            var $v = "date_modif_" + id;
            $log.log('$scope.' + $v + ' = ' + '1');
            eval('$scope. ' + $v + ' = ' + '1');
        };
        $scope.modifdatecloture = function(id) {
            $log.log("in modifdatecloture");
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
        $scope.showinvitintervenant = function(id) {
            $log.log("in showinvitintervenant");
            var $v = "invit_interv_" + id;
            $log.log('$scope.' + $v + ' = ' + '1');
            eval('$scope. ' + $v + ' = ' + '1');
        };
        $scope.invitintervenant = function(id) {
            $log.log("in showinvitintervenant");
            var $nom = eval('$scope.evenements.nom_intervenant_' + id);
            var $prenom = eval('$scope.evenements.prenom_intervenant_' + id);
            var $email = eval('$scope.evenements.email_intervenant_' + id);
            var $msg = eval('$scope.evenements.msg_' + id);
            if (typeof $nom === 'undefined' || typeof $email === 'undefined' || !$nom || !$nom.length || !$email || !$email.length) {
                alert("Vous devez renseigner au moins nom et email !"); return;
            }
            if (typeof $prenom === 'undefined') $prenom = '';
            if (typeof $msg === 'undefined') $msg = '';
            $nom = $nom.replace(/(^\s+|\s+$)/g, '');
            $prenom = $prenom.replace(/(^\s+|\s+$)/g, '');
            $email = $email.replace(/(^\s+|\s+$)/g, '');
            $msg = $msg.replace(/(^\s+|\s+$)/g, '');
            if (!$nom.length || !$email.length) {
                alert("Vous devez renseigner au moins nom et email !"); return;
            }
            $log.log('nom=' + $nom);
            $log.log($scope.evenements.nom_intervenant_1);
            var $params = {"id" : id, "nom" : $nom, "prenom" : $prenom, email : $email, "message" : $msg};
            $log.log($params);
            $http.get('/api/invitintervenant', {'params': $params}).then(function(resp) {
                if (resp.data == true) { alert("La personne a bien été invitée"); return; }
                else if (resp.data == false) { alert("La personne a bien reçu un mail, mais elle était déjà invitée..."); return; }
                else { $log.log(resp.data); $log.log(typeof resp.data); }
            });
            var $v = "invit_interv_" + id;
            $log.log('$scope.' + $v + ' = ' + '0');
            eval('$scope. ' + $v + ' = ' + '0');
        };
    }]);

var newevt = angular.module('newevt',['pickadate', '720kb.tooltips'])
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
    /*$scope.update = function(formulaire) {
        $log.log("in update");
        $scope.master = angular.copy(formulaire);
    };*/
    $scope.reset = function() {
        $log.log("in reset");
        ncollform.reset();
        $scope.formulaire = angular.copy($scope.master);
        $scope.formulaire.texte_restauration_1 = ncollform.texte_restauration_1.defaultValue;
    };
    //$scope.reset();
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
        if ($scope.date_fin != $scope.date) {
            $log.log("2 dates différentes");
            $scope.sur_plusieurs_jours = 1;
        }
        else $scope.sur_plusieurs_jours = 0;
        //document.forms[0]["evenement-lieu"].focus();
    };
    $scope.calc_date_ouverture_inscriptions = function() {
        $log.log("in calc_ouverture_inscriptions");
        $log.log("date_ouverture_inscriptions = " + $scope.formulaire.date_ouverture_inscriptions);
        if ($scope.ncollform.date && (calcule_date($scope.formulaire.date_ouverture_inscriptions) > calcule_date($scope.ncollform.date))) {
            alert("La date d'ouverture des inscriptions est postérieure à la date de l'évenement !");
        }
        $scope.date_ouverture_inscriptions = $scope.formulaire.date_ouverture_inscriptions;
        //document.forms[0]["date_cloture_inscriptions"].focus();
    };
    $scope.calc_date_cloture_inscriptions = function() {
        $log.log("in calc_date_cloture_inscriptions");
        if ($scope.formulaire.date_ouverture_inscriptions && $scope.formulaire.date_cloture_inscriptions && calcule_date($scope.formulaire.date_cloture_inscriptions) < calcule_date($scope.formulaire.date_ouverture_inscriptions)) {
            alert("La date de clôture ne peut pas être antérieure à la date d'ouverture !");
            $scope.date_cloture_inscriptions = $scope.formulaire.date_ouverture_inscriptions;
        }
        if ($scope.date_fin && $scope.formulaire.date_cloture_inscriptions && calcule_date($scope.formulaire.date_cloture_inscriptions) > calcule_date($scope.evenement.date_fin)) {
            alert("La date de clôture des inscriptions ne peut pas être postérieure à la date de fin de l'événement !");
            $scope.date_cloture_inscriptions = $scope.evenement.date_fin;
        }
        $scope.formulaire.date_cloture_inscriptions = $scope.formulaire.date_cloture_inscriptions;
    };
    $scope.click_texte_restauration_1 = function() {
        $log.log("in click_texte_restauration_1");
        if ($scope.formulaire.texte_restauration_1 == ncollform.texte_restauration_1.defaultValue) {
            $scope.formulaire.texte_restauration_1 = "";
        }
    };
    /* $log.log("tout lu"); */
}]);
