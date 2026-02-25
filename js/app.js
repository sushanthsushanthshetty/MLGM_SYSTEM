// Migrant Labor & Grievance Management System
// AngularJS Application Module

var app = angular.module('migrantApp', ['ngRoute']);

// Custom Filter: Capitalize
app.filter('capitalize', function() {
    return function(input) {
        if (!input) return '';
        return input.charAt(0).toUpperCase() + input.slice(1);
    };
});

// Configure Routes
app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'pages/home.html',
            controller: 'HomeController'
        })
        .when('/register', {
            templateUrl: 'pages/register.html',
            controller: 'RegisterController'
        })
        .when('/login', {
            templateUrl: 'pages/login.html',
            controller: 'LoginController'
        })
        .when('/dashboard', {
            templateUrl: 'pages/dashboard.html',
            controller: 'DashboardController'
        })
        .when('/profile', {
            templateUrl: 'pages/profile.html',
            controller: 'ProfileController'
        })
        .when('/complaint', {
            templateUrl: 'pages/complaint.html',
            controller: 'ComplaintController'
        })
        .when('/complaints', {
            templateUrl: 'pages/complaints.html',
            controller: 'ComplaintsController'
        })
        .when('/employers', {
            templateUrl: 'pages/employers.html',
            controller: 'EmployersController'
        })
        .when('/jobs', {
            templateUrl: 'pages/jobs.html',
            controller: 'JobsController'
        })
        .when('/applications', {
            templateUrl: 'pages/applications.html',
            controller: 'ApplicationsController'
        })
        .when('/admin-login', {
            templateUrl: 'pages/admin-login.html',
            controller: 'AdminLoginController'
        })
        .when('/admin-dashboard', {
            templateUrl: 'pages/admin-dashboard.html',
            controller: 'AdminDashboardController'
        })
        .when('/admin-applications', {
            templateUrl: 'pages/admin-applications.html',
            controller: 'AdminApplicationsController'
        })
        .when('/admin-complaints', {
            templateUrl: 'pages/admin-complaints.html',
            controller: 'AdminComplaintsController'
        })
        .when('/admin-employers', {
            templateUrl: 'pages/admin-employers.html',
            controller: 'AdminEmployersController'
        })
        .when('/employer-register', {
            templateUrl: 'pages/employer-register.html',
            controller: 'EmployerRegisterController'
        })
        .when('/employer-login', {
            templateUrl: 'pages/employer-login.html',
            controller: 'EmployerLoginController'
        })
        .when('/employer-dashboard', {
            templateUrl: 'pages/employer-dashboard.html',
            controller: 'EmployerDashboardController'
        })
        .otherwise({
            redirectTo: '/'
        });
}]);
