'use strict';
var flcollApp = angular.module('flcollApp', ['ngRoute', 'flform', 'suivi', 'newevt']);

flcollApp.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);

function desaccentue ($s) {
    $s = $s.replace(/[àáâä]/g,"a");
    $s = $s.replace(/ç/g,"c");
    $s = $s.replace(/[èéêë]/g,"e");
    $s = $s.replace(/[íîï]/g,"i");
    $s = $s.replace(/[ñ]/g,"n");
    $s = $s.replace(/[óôö]/g,"o");
    $s = $s.replace(/[ùûü]/g,"u");
    $s = $s.replace(/-/g," ");
    $s = $s.replace(/  /g," ");
    return $s;
}
function normalise_pour_comp($s) {
    return desaccentue($s.toLowerCase())
}

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

var suivi = angular.module('suivi',[])
.controller('suiviCtrl', ['$scope', '$log', '$http', function ($scope, $log, $http) {
    $log.log("in suivi");
}]);

var flform = angular.module('flform',[])
     .config(['$locationProvider',
             function($locationProvider) {
                 $locationProvider.html5Mode({
                     enabled: true,
                     requireBase: false
                 });
             }])
    .controller('flformCtrl', ['$scope', '$log', '$http', '$location', function ($scope, $log, $http, $location) {
        $log.log("in flform");
        $log.log($location.path());
        var $coll = $location.path().split("/").pop();
        $log.log($coll);
        $scope.master = {};
        $scope.cbadge1 = function(personne) {
            $log.log("in cbadge1");
            var $max1 = 27;
            var $p = ($scope.personne.prenom || "");
            $p = $p.charAt(0).toUpperCase() + $p.slice(1);
            var $n = ($scope.personne.nom || "");
            $n = $n.toUpperCase();
            var $badge1 = "";
            if ($p && $n) $badge1 = $p + " " + $n;
            else $badge1 = $p + $n;
            if ($badge1.length > $max1) {
                var $l1 = $badge1.length;
                if ($p) $p = $p.substr(0, $p.length - $l1 + $max1);
                else $n = $n.substr(0, $n.length - $l1 + $max1);
                if ($p && $n) $badge1 = $p + " " + $n;
                else $badge1 = $p + $n;
            }
            $scope.badge1 = $badge1;
        };
        $scope.cbadge2 = function(personne) {
            $log.log("in cbadge2");
            var $max2 = 33;
            var $f = ($scope.personne.fonction || "");
            var $o = ($scope.personne.organisation || "");
            var $badge2 = "";
            if ($f && $o) {
                $badge2 = $f + " - " + $o;
                if ($badge2.length > $max2) $badge2 = $f + "-" + $o;
            }
            else $badge2 = $f + $o;
            if ($badge2.length > $max2) {
                var $l2 = $badge2.length;
                if ($f) $f = $f.substr(0, $f.length - $l2 + $max2);
                else $o = $o.substr(0, $o.length - $l2 + $max2);
                if ($f && $o) $badge2 = $f + "-" + $o;
                else $badge2 = $f + $o;
            }
            $scope.badge2 = $badge2;
        };
        $scope.chkemail = function(personne) {
            $log.log("in chkemail");
            if ($scope.personne.nom && $scope.personne.email) {
                var $email_a_verifier = ($scope.personne.email || "");
                $log.log($email_a_verifier);
                /*var $params = {"email" : window.encodeURIComponent($email_a_verifier),
                               "nom" : window.encodeURIComponent($scope.personne.nom),
                               "prenom" : window.encodeURIComponent($scope.personne.prenom)}; */
                var $params = {"evt" : $coll, "email" : $email_a_verifier, "nom" : $scope.personne.nom, "prenom" : $scope.personne.prenom};
                $http.get('/api/chkemail', {'params': $params}).then(function(resp) {
                    $log.log(resp.data);
                    if (resp.data) {
                        $log.log(resp.data);
                        $log.log(resp.data[0]);
                        $log.log(resp.data[1]);
                        if (resp.data[0] && resp.data[0] != -1) $scope.personne.id = resp.data[0];
                        if (resp.data[1] && resp.data[1] == "oui") $scope.deja_inscrit = 1;
                        else $scope.deja_inscrit = 0;
                        if ($scope.deja_inscrit) {
                            $log.log("personne déjà inscrite");
                            $scope.msg_dejainscrit = "Vous êtes déjà inscrit-e à cet événement !";
                        }
                        else {
                            $log.log("email déjà dans la base mais personne pas encore inscrite");
                            delete $scope.msg_dejainscrit;
                            $scope.duplicateemail = "y";
                        }
                    }
                });
            }
        }
        $scope.envoi_email_verification = function(personne) {
            $log.log("in envoi_email_verification");
            $log.log("on envoie un mail à <" + $scope.personne.email + ">");
            var $params = {"email" : $scope.personne.email}
            $log.log(angular.toJson({"params": $params}));
            $http.get('/api/envoicodeverif', {'params': $params}).then(function(resp) {
                $log.log(resp.data); // FIXME POST
                if (resp.data) {
                    $scope.personne.emailsent = "y";
                    $scope.codeverifsrv = resp.data;
                    $log.log("codeverif=" + $scope.codeverifsrv);
                    delete $scope.duplicateemail;
                }
                else {
                    $scope.personne.id = null;
                    $scope.msg_duplicateemail = "erreur d'envoi du code de vérification";
                }
            });
        }
        $scope.verifier_code = function(personne) {
            $log.log("in verifier_code");
            $log.log($scope.personne.codeverif);
            delete $scope.personne.emailsent;
            if ($scope.personne.codeverif == $scope.codeverifsrv) { $scope.personne.codeok = "y"; delete $scope.personne.codeko; }
            else { $scope.personne.codeko = "y"; delete $scope.personne.codeok; }
        }
        $scope.reset = function(form) {
            $log.log("in reset");
            if (form) {
                form.$setPristine();
                form.$setUntouched();
            }
        };
        $scope.reset();
    }]);
