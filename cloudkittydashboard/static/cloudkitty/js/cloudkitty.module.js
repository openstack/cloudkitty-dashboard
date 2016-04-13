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
      workflow.append({
        formName: 'CloudkittyForm',
        templateUrl: '/dashboard/static/cloudkitty/templates/cloudkitty-step.html',
        helpUrl: '/dashboard/static/cloudkitty/templates/cloudkitty-help.html',
        title: 'Price'
      });
      return workflow;
   }]);

  }

})();
