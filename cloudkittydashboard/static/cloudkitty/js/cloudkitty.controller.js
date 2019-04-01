(function () {
  'use strict';

  angular
    .module('horizon.dashboard.cloudkitty')
    .controller('CloudkittyStepController', CloudkittyStepController);

  CloudkittyStepController.$inject = [
    '$scope',
    'horizon.framework.widgets.wizard.events',
    '$http',
    '$window'
  ];

  function CloudkittyStepController($scope, wizardEvents, $http, $window) {

    var onSwitch = $scope.$on(wizardEvents.ON_SWITCH, function(evt, args) {

      if(!$scope.model.newInstanceSpec.flavor) return false;

      var disk_total = $scope.model.newInstanceSpec.flavor.ephemeral + $scope.model.newInstanceSpec.flavor.disk;

      var desc_form = {
        'flavor_name': $scope.model.newInstanceSpec.flavor.name,
        'flavor_id': $scope.model.newInstanceSpec.flavor.id,
        'vcpus': $scope.model.newInstanceSpec.flavor.vcpus,
        'disk': $scope.model.newInstanceSpec.flavor.disk,
        'ephemeral': $scope.model.newInstanceSpec.flavor.ephemeral,
        'disk_total': disk_total,
        'disk_total_display': disk_total,
        'ram': $scope.model.newInstanceSpec.flavor.ram,
        'source_type': $scope.model.newInstanceSpec.source_type.type,
        'source_val': $scope.model.newInstanceSpec.source[0].id,
        'image_id': $scope.model.newInstanceSpec.source[0].id,
      }

      var form_data = [{"desc": desc_form, "volume": $scope.model.newInstanceSpec.instance_count}];

      $http.post($window.WEBROOT + 'project/rating/quote', form_data).then(function(res, status) {
        $scope.price = res.data;
      });
    });
  }

})();
