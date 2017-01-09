'use strict';
var flcollApp = angular.module('flcollApp', ['ngRoute', 'ui.bootstrap', 'flform', 'suivi', 'newevt']);

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
                // FIXME initialiser toutes les variables auxiliaires
                // (en profiter pour réduire leur nombre)
                var $email_a_verifier = ($scope.personne.email || "");
                $log.log($email_a_verifier);
                /* var $data = angular.toJson({'id_evenement': $coll});
                   $http.get('/api/inscription', {'data':$data}).then(function(resp) {
                   console.log(resp.data);
                   });*/
                var $filters = [{"name": "email", "op": "eq", "val": $email_a_verifier}];
                $http.get('/api/chkemail', {'params': {"q": angular.toJson({"filters": $filters})}}).then(function(resp) {
                    $log.log(resp.data);
                    //var $id_personne;
                    if (resp.data.num_results) {
                        $log.log(resp.data.objects[0]);
                        $scope.id_personne = resp.data.objects[0].id;
                        var $nom_bdd = resp.data.objects[0].nom;
                        var $prenom_bdd = resp.data.objects[0].prenom;
                        if (normalise_pour_comp($scope.personne.nom) != normalise_pour_comp($nom_bdd) || normalise_pour_comp($scope.personne.prenom) != normalise_pour_comp($prenom_bdd)) {
                            $log.log("nom ou prenom diff.");
                            $scope.personne.duplicateemail = "y";
                            $log.log($scope.personne.duplicateemail);
                        }
                        else {
                            var $filters = [{"name": "id_evenement", "op": "eq", "val": $coll},
                                        {"name": "id_personne", "op": "eq", "val": $scope.id_personne}];
                            $log.log($filters);
                            $http.get('/api/inscription', {'params': {"q": angular.toJson({"filters": $filters})}}).then(function(resp) {
                                $log.log(resp.data);
                                if (resp.data.num_results) {
                                    $log.log("personne déjà inscrite");
                                    $scope.msg_duplicateemail = "Vous êtes déjà inscrit-e à cet événement !";
                                }
                                else delete $scope.msg_duplicateemail;
                            }
                                                                                                                        )};
                    }
                });
            }
        }
        $scope.envoi_email_verification = function(personne) {
            $log.log("in envoi_email_verification");
            $log.log("on envoie un mail à <" + $scope.personne.email + ">");
            var $filters = [{"name": "id", "op": "eq", "val": $scope.id_personne}]
            $log.log(angular.toJson({"filters": $filters}));
            $http.get('/api/envoicodeverif', {'params': {"q": angular.toJson({"filters": $filters})}}).then(function(resp) {
                $log.log(resp.data); // FIXME POST
                if (resp.data.num_results) {
                    $log.log(resp.data.objects[0]);
                    $scope.codeverifsrv = resp.data.objects[0].envoi_mail_verif;
                    $log.log("codeverif=" + $scope.codeverifsrv);
                    $scope.personne.emailsent = "y";
                    delete $scope.personne.duplicateemail;
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
