(function () {
  'use strict';

  var ck = angular.module('horizon.dashboard.cloudkitty', ['horizon.dashboard.project.workflow']).config(config)

  config.$inject = [
    '$provide',
    '$windowProvider'
  ];

  function config($provide, $windowProvider) {

   $provide.decorator("horizon.dashboard.project.workflow.launch-instance.workflow", ['$delegate', function ($delegate) {
      var workflow = $delegate;
      var static_path = $windowProvider.$get().STATIC_URL;
      workflow.append({
        formName: 'CloudkittyForm',
        templateUrl: static_path + 'cloudkitty/templates/cloudkitty-step.html',
        helpUrl: static_path + 'cloudkitty/templates/cloudkitty-help.html',
        title: 'Price'
      });
      return workflow;
   }]);

  }

})();
