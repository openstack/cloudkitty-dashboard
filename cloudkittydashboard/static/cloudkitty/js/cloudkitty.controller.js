(function () {
  'use strict';

  angular
    .module('horizon.dashboard.cloudkitty')
    .controller('CloudkittyStepController', CloudkittyStepController);

  CloudkittyStepController.$inject = [
    '$scope',
    'horizon.framework.widgets.wizard.events',
    '$http',
    '$window',
    '$timeout'
  ];

  function CloudkittyStepController($scope, wizardEvents, $http, $window,
                                    $timeout) {
    var ctrl = this;
    var lastRequest = 0;
    var pending = null;

    ctrl.quote = null;
    ctrl.loading = false;
    ctrl.error = false;
    ctrl.hasFlavor = false;

    $scope.$on(wizardEvents.ON_SWITCH, refresh);

    $scope.$watch(signature, function (value, previous) {
      if (value !== previous) {
        if (pending) {
          $timeout.cancel(pending);
        }
        pending = $timeout(refresh, 300);
      }
    });
    refresh();

    function signature() {
      var spec = $scope.model && $scope.model.newInstanceSpec;
      if (!spec || !spec.flavor) {
        return '';
      }
      var source = (spec.source && spec.source[0]) || {};
      var volumeType = spec.vol_type || {};
      return [
        spec.flavor.id,
        spec.instance_count,
        spec.source_type && spec.source_type.type,
        source.id,
        spec.vol_create,
        spec.vol_size,
        volumeType.id
      ].join('|');
    }

    function buildItems(spec) {
      var flavor = spec.flavor;
      var source = (spec.source && spec.source[0]) || {};
      var count = parseInt(spec.instance_count, 10) || 1;
      var diskTotal = (flavor.ephemeral || 0) + (flavor.disk || 0);

      var items = [{
        kind: 'instance',
        name: flavor.name,
        volume: count,
        desc: {
          metadata: {
            'flavor_name': flavor.name,
            'flavor_id': flavor.id,
            'vcpus': flavor.vcpus,
            'disk': flavor.disk,
            'ephemeral': flavor.ephemeral,
            'disk_total': diskTotal,
            'disk_total_display': diskTotal,
            'ram': flavor.ram,
            'source_type': spec.source_type && spec.source_type.type,
            'source_val': source.id,
            'image_id': source.id
          }
        }
      }];

      // A new volume is created when booting from an image or a snapshot
      // with "Create New Volume" enabled.
      var volumeSize = parseInt(spec.vol_size, 10);
      if (spec.vol_create && volumeSize > 0) {
        var volumeType = spec.vol_type || {};
        items.push({
          kind: 'volume',
          name: volumeType.name || '',
          volume: volumeSize * count,
          desc: {
            metadata: {
              'volume_type_id': volumeType.id || '',
              'volume_type_name': volumeType.name || '',
              'size': volumeSize
            }
          }
        });
      }

      return items;
    }

    function refresh() {
      var spec = $scope.model && $scope.model.newInstanceSpec;
      ctrl.hasFlavor = !!(spec && spec.flavor);
      if (!ctrl.hasFlavor) {
        ctrl.quote = null;
        return;
      }

      var request = ++lastRequest;
      ctrl.loading = true;
      ctrl.error = false;

      $http.post($window.WEBROOT + 'project/rating/quote/details',
                 buildItems(spec)).then(function (res) {
        // Ignore answers to outdated requests.
        if (request !== lastRequest) {
          return;
        }
        ctrl.quote = res.data;
        ctrl.loading = false;
      }, function () {
        if (request !== lastRequest) {
          return;
        }
        ctrl.quote = null;
        ctrl.error = true;
        ctrl.loading = false;
      });
    }
  }

})();
