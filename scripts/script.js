// script.js
// create the module and name it brenoco
// also include ngRoute for all our routing needs

var brenoco = angular.module('brenoco', ['ngRoute', 'ngAnimate']);

// configure our routes
brenoco.config(function($routeProvider, $locationProvider) {
  $routeProvider
    // route for the home page
    .when('/', {
        templateUrl : 'pages/home.html',
        controller  : 'mainController'
    })

    // route for the about page
    .when('/about', {
        templateUrl : 'pages/about.html',
        controller  : 'aboutController'
    })

    // route for the projects page
    .when('/projects', {
        templateUrl : 'pages/projects.html',
        controller  : 'projectsController'
    })

    // route for the contact page
    .when('/contact', {
        templateUrl : 'pages/contact.html',
        controller  : 'contactController'
    });

    // use the HTML5 History API
    $locationProvider.html5Mode(true);
});

// create the controller and inject Angular's $scope
brenoco.controller('mainController', function($scope) {
  $scope.message = "pls don't break anything, i'm still working";
  $scope.pageClass = 'page-home';
});

brenoco.controller('aboutController', function($scope) {
  $scope.message = "here i'll put something nice about me (and maybe mechanical keyboards too)";
  $scope.pageClass = 'page-about';
});

brenoco.controller('projectsController', function($scope) {
  $scope.message = "here it'll be a list of my current projects";
  $scope.pageClass = 'page-projects';
});

brenoco.controller('contactController', function($scope) {
  $scope.message = "and here a nice contact form";
  $scope.pageClass = 'page-contact';
});