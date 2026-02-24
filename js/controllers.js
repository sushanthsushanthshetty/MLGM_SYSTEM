// =====================================================
// Migrant Labor & Grievance Management System (MLGMS)
// AngularJS Controllers - Connected to Flask Backend
// =====================================================

// API Base URL
var API_BASE_URL = 'http://localhost:5000/api';

// =====================================================
// Auth Service - Shared across controllers
// =====================================================
app.factory('AuthService', ['$http', '$window', function($http, $window) {
    var service = {};
    
    // Get session from localStorage
    service.getSession = function() {
        var session = $window.localStorage.getItem('mlgms_session');
        return session ? JSON.parse(session) : null;
    };
    
    // Set session in localStorage
    service.setSession = function(sessionData) {
        $window.localStorage.setItem('mlgms_session', JSON.stringify(sessionData));
    };
    
    // Clear session
    service.clearSession = function() {
        $window.localStorage.removeItem('mlgms_session');
    };
    
    // Check if logged in
    service.isLoggedIn = function() {
        return service.getSession() !== null;
    };
    
    // Get current worker
    service.getCurrentWorker = function() {
        var session = service.getSession();
        return session ? session.worker : null;
    };
    
    // Get auth header
    service.getAuthHeader = function() {
        var session = service.getSession();
        return session ? session.session_id : null;
    };
    
    return service;
}]);

// =====================================================
// HTTP Interceptor for Auth
// =====================================================
app.factory('AuthInterceptor', ['$q', '$window', function($q, $window) {
    return {
        request: function(config) {
            var session = $window.localStorage.getItem('mlgms_session');
            if (session) {
                var sessionData = JSON.parse(session);
                config.headers['Authorization'] = 'Bearer ' + sessionData.session_id;
            }
            return config;
        },
        responseError: function(response) {
            if (response.status === 401) {
                $window.localStorage.removeItem('mlgms_session');
            }
            return $q.reject(response);
        }
    };
}]);

app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.interceptors.push('AuthInterceptor');
}]);

// =====================================================
// Home Controller
// =====================================================
app.controller('HomeController', ['$scope', function($scope) {
    $scope.projectTitle = 'Migrant Labor & Grievance Management System';
    $scope.description = 'A comprehensive government portal for migrant workers to register, manage profiles, file complaints, and connect with employers. This system aims to protect the rights of migrant workers and ensure their grievances are addressed promptly.';
}]);

// =====================================================
// Register Controller
// =====================================================
app.controller('RegisterController', ['$scope', '$http', '$location', function($scope, $http, $location) {
    // Initialize form data
    $scope.formData = {
        name: '',
        phone: '',
        age: '',
        gender: '',
        skill: ''
    };
    
    // Gender options
    $scope.genderOptions = [
        { value: 'male', label: 'Male' },
        { value: 'female', label: 'Female' },
        { value: 'other', label: 'Other' }
    ];
    
    // Skill options
    $scope.skillOptions = [
        { value: 'electrician', label: 'Electrician' },
        { value: 'plumber', label: 'Plumber' },
        { value: 'carpenter', label: 'Carpenter' },
        { value: 'mason', label: 'Mason' },
        { value: 'painter', label: 'Painter' },
        { value: 'welder', label: 'Welder' },
        { value: 'driver', label: 'Driver' },
        { value: 'cook', label: 'Cook' },
        { value: 'cleaner', label: 'Cleaner' },
        { value: 'other', label: 'Other' }
    ];
    
    // Registration success flag
    $scope.registrationSuccess = false;
    $scope.migrantId = '';
    $scope.loading = false;
    $scope.errorMessage = '';
    
    // Register function
    $scope.register = function() {
        // Check if form is valid
        if ($scope.registerForm.$invalid) {
            $scope.registerForm.$setSubmitted();
            return;
        }
        
        $scope.loading = true;
        $scope.errorMessage = '';
        
        // Prepare data for API
        var requestData = {
            name: $scope.formData.name,
            phone: $scope.formData.phone,
            age: $scope.formData.age,
            gender: $scope.formData.gender,
            skill: $scope.formData.skill
        };
        
        // Call API
        $http.post(API_BASE_URL + '/register', requestData)
            .then(function(response) {
                if (response.data.success) {
                    $scope.registrationSuccess = true;
                    $scope.migrantId = response.data.migrant_id;
                } else {
                    $scope.errorMessage = response.data.message || 'Registration failed. Please try again.';
                }
            })
            .catch(function(error) {
                console.error('Complaint error:', error);
                if (error.status === 401) {
                    $scope.errorMessage = 'Please login again to submit a complaint.';
                    $location.path('/login');
                } else {
                    $scope.errorMessage = error.data?.message || 'An error occurred. Please try again.';
                }
            })
            .finally(function() {
                $scope.loading = false;
            });
    };
    
    // Reset form
    $scope.resetForm = function() {
        $scope.formData = {
            name: '',
            phone: '',
            age: '',
            gender: '',
            skill: ''
        };
        $scope.registrationSuccess = false;
        $scope.migrantId = '';
        $scope.errorMessage = '';
        if ($scope.registerForm) {
            $scope.registerForm.$setPristine();
            $scope.registerForm.$setUntouched();
        }
    };
}]);

// =====================================================
// Login Controller
// =====================================================
app.controller('LoginController', ['$scope', '$http', '$location', 'AuthService', function($scope, $http, $location, AuthService) {
    // Initialize login data
    $scope.loginData = {
        migrantId: '',
        phone: ''
    };
    
    $scope.loading = false;
    $scope.errorMessage = '';
    
    // Login function
    $scope.login = function() {
        if ($scope.loginForm.$invalid) {
            return;
        }
        
        $scope.loading = true;
        $scope.errorMessage = '';
        
        var requestData = {
            migrant_id: $scope.loginData.migrantId.toUpperCase(),
            phone: $scope.loginData.phone
        };
        
        $http.post(API_BASE_URL + '/login', requestData)
            .then(function(response) {
                if (response.data.success) {
                    // Store session
                    AuthService.setSession(response.data);
                    // Navigate to dashboard
                    $location.path('/dashboard');
                } else {
                    $scope.errorMessage = response.data.message || 'Login failed. Please try again.';
                }
            })
            .catch(function(error) {
                $scope.errorMessage = error.data?.message || 'Invalid credentials. Please try again.';
            })
            .finally(function() {
                $scope.loading = false;
            });
    };
}]);

// =====================================================
// Dashboard Controller
// =====================================================
app.controller('DashboardController', ['$scope', '$http', '$location', 'AuthService', function($scope, $http, $location, AuthService) {
    // Check if logged in
    if (!AuthService.isLoggedIn()) {
        $location.path('/login');
        return;
    }
    
    // Get current worker
    var currentWorker = AuthService.getCurrentWorker();
    
    // Dashboard menu items
    $scope.menuItems = [
        { title: 'Find Work', icon: '💼', link: '#!/jobs', color: '#17a2b8' },
        { title: 'My Applications', icon: '📄', link: '#!/applications', color: '#6610f2' },
        { title: 'My Profile', icon: '👤', link: '#!/profile', color: '#0d6efd' },
        { title: 'File Complaint', icon: '📝', link: '#!/complaint', color: '#dc3545' },
        { title: 'My Complaints', icon: '📋', link: '#!/complaints', color: '#ffc107' },
        { title: 'Employer List', icon: '🏢', link: '#!/employers', color: '#28a745' },
        { title: 'Logout', icon: '🚪', link: '#!/', color: '#6c757d' }
    ];
    
    // Dashboard stats
    $scope.worker = currentWorker;
    $scope.stats = {
        total: 0,
        pending: 0,
        resolved: 0
    };
    $scope.loading = true;
    
    // Load dashboard data
    $http.get(API_BASE_URL + '/dashboard/current')
        .then(function(response) {
            if (response.data.success) {
                $scope.worker = response.data.worker;
                $scope.stats = response.data.stats;
            }
        })
        .catch(function(error) {
            console.error('Error loading dashboard:', error);
        })
        .finally(function() {
            $scope.loading = false;
        });
    
    // Navigate to page
    $scope.navigateTo = function(link) {
        var path = link.replace('#!/', '');
        if (path === '/') {
            // Logout
            $http.post(API_BASE_URL + '/logout')
                .then(function() {
                    AuthService.clearSession();
                    $location.path('/');
                })
                .catch(function() {
                    AuthService.clearSession();
                    $location.path('/');
                });
        } else {
            $location.path(path);
        }
    };
    
    // Logout function
    $scope.logout = function() {
        $http.post(API_BASE_URL + '/logout')
            .then(function() {
                AuthService.clearSession();
                $location.path('/');
            })
            .catch(function() {
                AuthService.clearSession();
                $location.path('/');
            });
    };
}]);

// =====================================================
// Profile Controller
// =====================================================
app.controller('ProfileController', ['$scope', '$http', '$location', 'AuthService', function($scope, $http, $location, AuthService) {
    // Check if logged in
    if (!AuthService.isLoggedIn()) {
        $location.path('/login');
        return;
    }
    
    var currentWorker = AuthService.getCurrentWorker();
    
    $scope.worker = null;
    $scope.loading = true;
    $scope.editMode = false;
    $scope.updateSuccess = false;
    $scope.updateError = '';
    
    // Edit form data
    $scope.editData = {};
    
    // Gender options
    $scope.genderOptions = [
        { value: 'male', label: 'Male' },
        { value: 'female', label: 'Female' },
        { value: 'other', label: 'Other' }
    ];
    
    // Load profile data
    $http.get(API_BASE_URL + '/profile')
        .then(function(response) {
            if (response.data.success) {
                $scope.worker = response.data.worker;
            }
        })
        .catch(function(error) {
            console.error('Error loading profile:', error);
        })
        .finally(function() {
            $scope.loading = false;
        });
    
    // Enable edit mode
    $scope.enableEdit = function() {
        $scope.editMode = true;
        $scope.editData = {
            name: $scope.worker.name,
            phone: $scope.worker.phone,
            age: $scope.worker.age,
            gender: $scope.worker.gender,
            skill: $scope.worker.skill,
            state: $scope.worker.state,
            district: $scope.worker.district,
            address: $scope.worker.address
        };
        $scope.updateSuccess = false;
        $scope.updateError = '';
    };
    
    // Cancel edit
    $scope.cancelEdit = function() {
        $scope.editMode = false;
        $scope.updateSuccess = false;
        $scope.updateError = '';
    };
    
    // Update profile
    $scope.updateProfile = function() {
        $scope.updateSuccess = false;
        $scope.updateError = '';
        
        $http.put(API_BASE_URL + '/profile/update', $scope.editData)
            .then(function(response) {
                if (response.data.success) {
                    $scope.worker = response.data.worker;
                    $scope.editMode = false;
                    $scope.updateSuccess = true;
                } else {
                    $scope.updateError = response.data.message || 'Failed to update profile.';
                }
            })
            .catch(function(error) {
                $scope.updateError = error.data?.message || 'An error occurred while updating.';
            });
    };
}]);

// =====================================================
// Complaint Controller
// =====================================================
app.controller('ComplaintController', ['$scope', '$http', '$location', 'AuthService', function($scope, $http, $location, AuthService) {
    // Check if logged in
    if (!AuthService.isLoggedIn()) {
        $location.path('/login');
        return;
    }
    
    // Initialize complaint data
    $scope.complaintData = {
        type: '',
        description: ''
    };
    
    // Complaint type options
    $scope.complaintTypes = [
        { value: 'wages', label: 'Non-Payment of Wages' },
        { value: 'safety', label: 'Safety Issues' },
        { value: 'harassment', label: 'Workplace Harassment' },
        { value: 'accommodation', label: 'Accommodation Problems' },
        { value: 'working_hours', label: 'Excessive Working Hours' },
        { value: 'contract', label: 'Contract Violation' },
        { value: 'other', label: 'Other' }
    ];
    
    // Submission flags
    $scope.submissionSuccess = false;
    $scope.loading = false;
    $scope.errorMessage = '';
    $scope.complaintId = '';
    
    // Submit complaint function
    $scope.submitComplaint = function() {
        if ($scope.complaintForm.$invalid) {
            $scope.complaintForm.$setSubmitted();
            return;
        }
        
        // Client-side validation
        if (!$scope.complaintData.type) {
            $scope.errorMessage = 'Please select a complaint type.';
            return;
        }
        
        if (!$scope.complaintData.description || $scope.complaintData.description.length < 10) {
            $scope.errorMessage = 'Description must be at least 10 characters.';
            return;
        }
        
        $scope.loading = true;
        $scope.errorMessage = '';
        
        var requestData = {
            type: $scope.complaintData.type,
            description: $scope.complaintData.description
        };
        
        console.log('Submitting complaint:', requestData);
        
        $http.post(API_BASE_URL + '/complaint/add', requestData)
            .then(function(response) {
                if (response.data.success) {
                    $scope.submissionSuccess = true;
                    $scope.complaintId = response.data.complaint_id;
                } else {
                    $scope.errorMessage = response.data.message || 'Failed to submit complaint.';
                }
            })
            .catch(function(error) {
                $scope.errorMessage = error.data?.message || 'An error occurred. Please try again.';
            })
            .finally(function() {
                $scope.loading = false;
            });
    };
    
    // Reset form
    $scope.resetForm = function() {
        $scope.complaintData = {
            type: '',
            description: ''
        };
        $scope.submissionSuccess = false;
        $scope.complaintId = '';
        $scope.errorMessage = '';
        if ($scope.complaintForm) {
            $scope.complaintForm.$setPristine();
            $scope.complaintForm.$setUntouched();
        }
    };
}]);

// =====================================================
// Complaints List Controller
// =====================================================
app.controller('ComplaintsController', ['$scope', '$http', '$location', 'AuthService', function($scope, $http, $location, AuthService) {
    // Check if logged in
    if (!AuthService.isLoggedIn()) {
        $location.path('/login');
        return;
    }
    
    $scope.complaints = [];
    $scope.loading = true;
    $scope.errorMessage = '';
    
    // Load complaints
    $http.get(API_BASE_URL + '/complaint/list')
        .then(function(response) {
            if (response.data.success) {
                $scope.complaints = response.data.complaints;
            }
        })
        .catch(function(error) {
            $scope.errorMessage = 'Error loading complaints.';
            console.error('Error loading complaints:', error);
        })
        .finally(function() {
            $scope.loading = false;
        });
    
    // Get status class
    $scope.getStatusClass = function(status) {
        if (status === 'Pending') {
            return 'status-pending';
        } else if (status === 'Resolved') {
            return 'status-resolved';
        }
        return '';
    };
}]);

// =====================================================
// Employers Controller
// =====================================================
app.controller('EmployersController', ['$scope', '$http', '$location', 'AuthService', function($scope, $http, $location, AuthService) {
    // Check if logged in
    if (!AuthService.isLoggedIn()) {
        $location.path('/login');
        return;
    }
    
    $scope.employers = [];
    $scope.loading = true;
    $scope.errorMessage = '';
    
    // Load employers
    $http.get(API_BASE_URL + '/employers/list')
        .then(function(response) {
            if (response.data.success) {
                $scope.employers = response.data.employers;
            }
        })
        .catch(function(error) {
            $scope.errorMessage = 'Error loading employers.';
            console.error('Error loading employers:', error);
        })
        .finally(function() {
            $scope.loading = false;
        });
    
    // Get status class
    $scope.getStatusClass = function(status) {
        if (status === 'Active') {
            return 'status-active';
        } else {
            return 'status-inactive';
        }
    };
    
    // Generate star rating
    $scope.getStars = function(rating) {
        var stars = '';
        var fullStars = Math.floor(rating);
        var halfStar = rating % 1 >= 0.5;
        
        for (var i = 0; i < fullStars; i++) {
            stars += '★';
        }
        if (halfStar) {
            stars += '☆';
        }
        for (var i = fullStars + (halfStar ? 1 : 0); i < 5; i++) {
            stars += '☆';
        }
        return stars;
    };
}]);

// =====================================================
// Jobs Controller - Find Work
// =====================================================
app.controller('JobsController', ['$scope', '$http', '$location', 'AuthService', function($scope, $http, $location, AuthService) {
    // Check if logged in
    if (!AuthService.isLoggedIn()) {
        $location.path('/login');
        return;
    }
    
    $scope.jobs = [];
    $scope.loading = true;
    $scope.errorMessage = '';
    $scope.filterSkill = '';
    
    // Skill options for filter
    $scope.skillOptions = [
        { value: 'electrician', label: 'Electrician' },
        { value: 'plumber', label: 'Plumber' },
        { value: 'carpenter', label: 'Carpenter' },
        { value: 'mason', label: 'Mason' },
        { value: 'painter', label: 'Painter' },
        { value: 'welder', label: 'Welder' },
        { value: 'driver', label: 'Driver' },
        { value: 'cook', label: 'Cook' },
        { value: 'cleaner', label: 'Cleaner' },
        { value: 'other', label: 'Other' }
    ];
    
    // Application stats
    $scope.appStats = {
        total: 0,
        pending: 0,
        accepted: 0,
        rejected: 0
    };
    
    // Load jobs
    $scope.loadJobs = function() {
        $scope.loading = true;
        var url = API_BASE_URL + '/jobs/list?status=open';
        if ($scope.filterSkill) {
            url += '&skill=' + $scope.filterSkill;
        }
        
        $http.get(url)
            .then(function(response) {
                if (response.data.success) {
                    $scope.jobs = response.data.jobs;
                }
            })
            .catch(function(error) {
                $scope.errorMessage = 'Error loading jobs.';
                console.error('Error loading jobs:', error);
            })
            .finally(function() {
                $scope.loading = false;
            });
    };
    
    // Load application stats
    $scope.loadAppStats = function() {
        $http.get(API_BASE_URL + '/jobs/applications/stats')
            .then(function(response) {
                if (response.data.success) {
                    $scope.appStats = response.data.stats;
                }
            })
            .catch(function(error) {
                console.error('Error loading application stats:', error);
            });
    };
    
    // Filter jobs
    $scope.filterJobs = function() {
        $scope.loadJobs();
    };
    
    // Apply for job
    $scope.applyForJob = function(job) {
        job.applying = true;
        
        $http.post(API_BASE_URL + '/jobs/apply/' + job.id)
            .then(function(response) {
                if (response.data.success) {
                    alert('Application submitted successfully! Application ID: ' + response.data.application_id);
                    $scope.loadAppStats();
                } else {
                    alert(response.data.message || 'Failed to apply for job.');
                }
            })
            .catch(function(error) {
                alert(error.data?.message || 'An error occurred. Please try again.');
            })
            .finally(function() {
                job.applying = false;
            });
    };
    
    // Initial load
    $scope.loadJobs();
    $scope.loadAppStats();
}]);

// =====================================================
// Applications Controller - My Applications
// =====================================================
app.controller('ApplicationsController', ['$scope', '$http', '$location', 'AuthService', function($scope, $http, $location, AuthService) {
    // Check if logged in
    if (!AuthService.isLoggedIn()) {
        $location.path('/login');
        return;
    }
    
    $scope.applications = [];
    $scope.loading = true;
    $scope.errorMessage = '';
    
    // Stats
    $scope.stats = {
        total: 0,
        pending: 0,
        accepted: 0,
        rejected: 0
    };
    
    // Load applications
    $http.get(API_BASE_URL + '/jobs/applications')
        .then(function(response) {
            if (response.data.success) {
                $scope.applications = response.data.applications;
            }
        })
        .catch(function(error) {
            $scope.errorMessage = 'Error loading applications.';
            console.error('Error loading applications:', error);
        })
        .finally(function() {
            $scope.loading = false;
        });
    
    // Load stats
    $http.get(API_BASE_URL + '/jobs/applications/stats')
        .then(function(response) {
            if (response.data.success) {
                $scope.stats = response.data.stats;
            }
        })
        .catch(function(error) {
            console.error('Error loading application stats:', error);
        });
}]);

// =====================================================
// Capitalize Filter
// =====================================================
app.filter('capitalize', function() {
    return function(input) {
        if (!input) return '';
        return input.charAt(0).toUpperCase() + input.slice(1);
    };
});

// =====================================================
// Admin Login Controller
// =====================================================
app.controller('AdminLoginController', ['$scope', '$http', '$location', '$window', function($scope, $http, $location, $window) {
    $scope.loginData = {
        username: '',
        password: ''
    };
    $scope.loading = false;
    $scope.errorMessage = '';
    
    $scope.adminLogin = function() {
        if ($scope.adminLoginForm.$invalid) {
            return;
        }
        
        $scope.loading = true;
        $scope.errorMessage = '';
        
        $http.post(API_BASE_URL + '/admin/login', $scope.loginData)
            .then(function(response) {
                if (response.data.success) {
                    $window.localStorage.setItem('mlgms_admin', JSON.stringify(response.data.admin));
                    $location.path('/admin-dashboard');
                } else {
                    $scope.errorMessage = response.data.message || 'Login failed.';
                }
            })
            .catch(function(error) {
                $scope.errorMessage = error.data?.message || 'Invalid credentials.';
            })
            .finally(function() {
                $scope.loading = false;
            });
    };
}]);

// =====================================================
// Admin Dashboard Controller
// =====================================================
app.controller('AdminDashboardController', ['$scope', '$http', '$location', '$window', function($scope, $http, $location, $window) {
    // Check if admin is logged in
    var admin = $window.localStorage.getItem('mlgms_admin');
    if (!admin) {
        $location.path('/admin-login');
        return;
    }
    
    $scope.admin = JSON.parse(admin);
    $scope.stats = {};
    $scope.recentApplications = [];
    $scope.loading = true;
    
    // Load stats
    $http.get(API_BASE_URL + '/admin/stats')
        .then(function(response) {
            if (response.data.success) {
                $scope.stats = response.data.stats;
            }
        })
        .catch(function(error) {
            console.error('Error loading stats:', error);
        });
    
    // Load recent applications
    $http.get(API_BASE_URL + '/admin/applications')
        .then(function(response) {
            if (response.data.success) {
                $scope.recentApplications = response.data.applications.slice(0, 5);
            }
        })
        .catch(function(error) {
            console.error('Error loading applications:', error);
        })
        .finally(function() {
            $scope.loading = false;
        });
    
    // Navigate to page
    $scope.navigateTo = function(path) {
        $location.path('/' + path);
    };
    
    // Accept application
    $scope.acceptApp = function(app) {
        $http.post(API_BASE_URL + '/admin/applications/' + app.id + '/accept')
            .then(function(response) {
                if (response.data.success) {
                    app.status = 'Accepted';
                    // Reload stats
                    $http.get(API_BASE_URL + '/admin/stats').then(function(res) {
                        if (res.data.success) {
                            $scope.stats = res.data.stats;
                        }
                    });
                }
            })
            .catch(function(error) {
                alert('Error accepting application');
            });
    };
    
    // Reject application
    $scope.rejectApp = function(app) {
        $http.post(API_BASE_URL + '/admin/applications/' + app.id + '/reject')
            .then(function(response) {
                if (response.data.success) {
                    app.status = 'Rejected';
                }
            })
            .catch(function(error) {
                alert('Error rejecting application');
            });
    };
    
    // Logout
    $scope.adminLogout = function() {
        $window.localStorage.removeItem('mlgms_admin');
        $location.path('/');
    };
}]);

// =====================================================
// Admin Applications Controller
// =====================================================
app.controller('AdminApplicationsController', ['$scope', '$http', '$location', '$window', function($scope, $http, $location, $window) {
    // Check if admin is logged in
    var admin = $window.localStorage.getItem('mlgms_admin');
    if (!admin) {
        $location.path('/admin-login');
        return;
    }
    
    $scope.applications = [];
    $scope.filterStatus = 'pending';
    $scope.loading = true;
    
    // Load applications
    $scope.loadApplications = function() {
        $scope.loading = true;
        var url = API_BASE_URL + '/admin/applications';
        if ($scope.filterStatus) {
            url += '?status=' + $scope.filterStatus;
        }
        
        $http.get(url)
            .then(function(response) {
                if (response.data.success) {
                    $scope.applications = response.data.applications;
                }
            })
            .catch(function(error) {
                console.error('Error loading applications:', error);
            })
            .finally(function() {
                $scope.loading = false;
            });
    };
    
    // Accept application
    $scope.acceptApplication = function(app) {
        app.processing = true;
        $http.post(API_BASE_URL + '/admin/applications/' + app.id + '/accept')
            .then(function(response) {
                if (response.data.success) {
                    app.status = 'Accepted';
                    app.processing = false;
                }
            })
            .catch(function(error) {
                alert('Error accepting application');
                app.processing = false;
            });
    };
    
    // Reject application
    $scope.rejectApplication = function(app) {
        app.processing = true;
        $http.post(API_BASE_URL + '/admin/applications/' + app.id + '/reject')
            .then(function(response) {
                if (response.data.success) {
                    app.status = 'Rejected';
                    app.processing = false;
                }
            })
            .catch(function(error) {
                alert('Error rejecting application');
                app.processing = false;
            });
    };
    
    // Initial load
    $scope.loadApplications();
}]);

// =====================================================
// Admin Complaints Controller
// =====================================================
app.controller('AdminComplaintsController', ['$scope', '$http', '$location', '$window', function($scope, $http, $location, $window) {
    // Check if admin is logged in
    var admin = $window.localStorage.getItem('mlgms_admin');
    if (!admin) {
        $location.path('/admin-login');
        return;
    }
    
    $scope.complaints = [];
    $scope.filterStatus = 'pending';
    $scope.loading = true;
    
    // Load complaints
    $scope.loadComplaints = function() {
        $scope.loading = true;
        var url = API_BASE_URL + '/admin/complaints';
        if ($scope.filterStatus) {
            url += '?status=' + $scope.filterStatus;
        }
        
        $http.get(url)
            .then(function(response) {
                if (response.data.success) {
                    $scope.complaints = response.data.complaints;
                }
            })
            .catch(function(error) {
                console.error('Error loading complaints:', error);
            })
            .finally(function() {
                $scope.loading = false;
            });
    };
    
    // Resolve complaint
    $scope.resolveComplaint = function(complaint) {
        complaint.processing = true;
        $http.post(API_BASE_URL + '/admin/complaints/' + complaint.id + '/resolve')
            .then(function(response) {
                if (response.data.success) {
                    complaint.status = 'resolved';
                    complaint.processing = false;
                }
            })
            .catch(function(error) {
                alert('Error resolving complaint');
                complaint.processing = false;
            });
    };
    
    // Initial load
    $scope.loadComplaints();
}]);
