'use strict';
var socoApp = angular.module('socoApp', ['ngRoute', 'flform']);

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
        //$log.log($location.path());
        var $ppath = $location.path().split("/");
        var $coll = $ppath.pop();
        if ($coll.length > 8) { var $tok = $coll; $coll = $ppath.pop(); }
        $log.log($coll);
        /* $scope.master = {}; */
        function calcule_badge1($prenom, $nom) {
            if ($prenom == undefined) $prenom = "";
            if ($nom == undefined) $nom = "";
            var $max1 = 27;
            var $p = $prenom.charAt(0).toUpperCase() + $prenom.toLowerCase().slice(1);
	    // FIXME faire une boucle pour repérer les ' ' et les '-'
            var $n = $nom.toUpperCase();
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
            return $badge1;
        }
        $scope.setspeaker = function(personne) {
            $log.log("in setspeaker");
            var $params = {"evt" : $coll, "token" : $tok};
            $http.get('/api/infoinscription', {'params': $params}).then(function(resp) {
                //$log.log(resp.data);
                if (resp.data) {
                    $scope.personne = resp.data;
                    $scope.badge1 = calcule_badge1(resp.data['prenom'] + ' ' + resp.data['nom']);
                }
            });
        }
        $scope.cbadge1 = function(personne) {
            $log.log("in cbadge1");
            $scope.badge1 = calcule_badge1($scope.personne.prenom, $scope.personne.nom);
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
                var $params = {"evt" : $coll, "email" : $email_a_verifier, "nom" : $scope.personne.nom, "prenom" : $scope.personne.prenom};
                $http.get('/api/chkemail', {'params': $params}).then(function(resp) {
                    $log.log(resp.data);
                    if (resp.data) {
                        if (resp.data[0] && resp.data[0] != -1) {
                            $scope.personne.id = resp.data[0];
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
                        else $log.log("l'email n'est pas dans la base");
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
