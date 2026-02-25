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


// =====================================================
// Employer Register Controller
// =====================================================
app.controller('EmployerRegisterController', ['$scope', '$http', '$location', function($scope, $http, $location) {
    // Initialize form data
    $scope.formData = {
        company_name: '',
        industry: '',
        location: '',
        contact_person: '',
        phone: '',
        email: '',
        password: '',
        confirm_password: '',
        gst_number: '',
        registration_number: '',
        address: ''
    };
    
    $scope.registrationSuccess = false;
    $scope.employerId = '';
    $scope.loading = false;
    $scope.errorMessage = '';
    
    // Register function
    $scope.register = function() {
        if ($scope.registerForm.$invalid) {
            $scope.registerForm.$setSubmitted();
            return;
        }
        
        // Check password match
        if ($scope.formData.password !== $scope.formData.confirm_password) {
            $scope.errorMessage = 'Passwords do not match';
            return;
        }
        
        $scope.loading = true;
        $scope.errorMessage = '';
        
        $http.post(API_BASE_URL + '/employers/register', $scope.formData)
            .then(function(response) {
                if (response.data.success) {
                    $scope.registrationSuccess = true;
                    $scope.employerId = response.data.employer_id;
                } else {
                    $scope.errorMessage = response.data.message || 'Registration failed. Please try again.';
                }
            })
            .catch(function(error) {
                $scope.errorMessage = error.data?.message || 'An error occurred. Please try again.';
            })
            .finally(function() {
                $scope.loading = false;
            });
    };
    
    // Go to login
    $scope.goToLogin = function() {
        $location.path('/employer-login');
    };
}]);


// =====================================================
// Employer Login Controller
// =====================================================
app.controller('EmployerLoginController', ['$scope', '$http', '$location', '$window', function($scope, $http, $location, $window) {
    // Initialize login data
    $scope.loginData = {
        employer_id: '',
        password: ''
    };
    
    $scope.loading = false;
    $scope.errorMessage = '';
    $scope.pendingVerification = false;
    $scope.rejectedAccount = false;
    
    // Login function
    $scope.login = function() {
        if ($scope.loginForm.$invalid) {
            return;
        }
        
        $scope.loading = true;
        $scope.errorMessage = '';
        $scope.pendingVerification = false;
        $scope.rejectedAccount = false;
        
        $http.post(API_BASE_URL + '/employers/login', {
            employer_id: $scope.loginData.employer_id.toUpperCase(),
            password: $scope.loginData.password
        })
            .then(function(response) {
                if (response.data.success) {
                    $window.localStorage.setItem('mlgms_employer', JSON.stringify(response.data.employer));
                    $location.path('/employer-dashboard');
                } else {
                    $scope.errorMessage = response.data.message || 'Login failed.';
                }
            })
            .catch(function(error) {
                if (error.status === 403) {
                    // Check verification status
                    if (error.data.verification_status === 'pending') {
                        $scope.pendingVerification = true;
                        $scope.employerId = $scope.loginData.employer_id.toUpperCase();
                    } else if (error.data.verification_status === 'rejected') {
                        $scope.rejectedAccount = true;
                        $scope.employerId = $scope.loginData.employer_id.toUpperCase();
                    } else {
                        $scope.errorMessage = error.data.message;
                    }
                } else {
                    $scope.errorMessage = error.data?.message || 'Invalid credentials.';
                }
            })
            .finally(function() {
                $scope.loading = false;
            });
    };
    
    // Check again
    $scope.checkAgain = function() {
        $scope.pendingVerification = false;
        $scope.login();
    };
}]);


// =====================================================
// Employer Dashboard Controller
// =====================================================
app.controller('EmployerDashboardController', ['$scope', '$http', '$location', '$window', function($scope, $http, $location, $window) {
    // Check if employer is logged in
    var employerSession = $window.localStorage.getItem('mlgms_employer');
    if (!employerSession) {
        $location.path('/employer-login');
        return;
    }
    
    $scope.employer = JSON.parse(employerSession);
    $scope.job_stats = {};
    $scope.application_stats = {};
    $scope.recentApplications = [];
    $scope.loading = true;
    $scope.showPostJob = false;
    $scope.jobData = {};
    $scope.postingJob = false;
    $scope.jobError = '';
    $scope.jobSuccess = '';
    
    // Load dashboard data
    $http.get(API_BASE_URL + '/employers/dashboard')
        .then(function(response) {
            if (response.data.success) {
                $scope.employer = response.data.employer;
                $scope.job_stats = response.data.job_stats;
                $scope.application_stats = response.data.application_stats;
                $scope.recentApplications = response.data.recent_applications;
            }
        })
        .catch(function(error) {
            console.error('Error loading dashboard:', error);
            if (error.status === 401 || error.status === 403) {
                $window.localStorage.removeItem('mlgms_employer');
                $location.path('/employer-login');
            }
        })
        .finally(function() {
            $scope.loading = false;
        });
    
    // Navigate to page
    $scope.navigateTo = function(path) {
        $location.path('/' + path);
    };
    
    // Logout
    $scope.logout = function() {
        $http.post(API_BASE_URL + '/employers/logout')
            .then(function() {
                $window.localStorage.removeItem('mlgms_employer');
                $location.path('/');
            })
            .catch(function() {
                $window.localStorage.removeItem('mlgms_employer');
                $location.path('/');
            });
    };
    
    // Post job
    $scope.postJob = function() {
        $scope.jobError = '';
        $scope.jobSuccess = '';
        
        if ($scope.jobForm.$invalid) {
            return;
        }
        
        $scope.postingJob = true;
        
        $http.post(API_BASE_URL + '/employers/jobs', $scope.jobData)
            .then(function(response) {
                if (response.data.success) {
                    $scope.jobSuccess = 'Job posted successfully! Job ID: ' + response.data.job_id;
                    $scope.jobData = {};
                    // Reload stats
                    $http.get(API_BASE_URL + '/employers/dashboard')
                        .then(function(res) {
                            if (res.data.success) {
                                $scope.job_stats = res.data.job_stats;
                            }
                        });
                    setTimeout(function() {
                        $scope.showPostJob = false;
                        $scope.jobSuccess = '';
                        $scope.$apply();
                    }, 2000);
                } else {
                    $scope.jobError = response.data.message || 'Failed to post job.';
                }
            })
            .catch(function(error) {
                $scope.jobError = error.data?.message || 'Error posting job.';
            })
            .finally(function() {
                $scope.postingJob = false;
            });
    };
    
    // Accept application
    $scope.acceptApp = function(app) {
        $http.post(API_BASE_URL + '/employers/applications/' + app.id + '/accept')
            .then(function(response) {
                if (response.data.success) {
                    app.status = 'accepted';
                    // Reload stats
                    $http.get(API_BASE_URL + '/employers/dashboard')
                        .then(function(res) {
                            if (res.data.success) {
                                $scope.application_stats = res.data.application_stats;
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
        $http.post(API_BASE_URL + '/employers/applications/' + app.id + '/reject')
            .then(function(response) {
                if (response.data.success) {
                    app.status = 'rejected';
                }
            })
            .catch(function(error) {
                alert('Error rejecting application');
            });
    };
    
    // Generate stars
    $scope.getStars = function(rating) {
        var stars = '';
        var fullStars = Math.floor(rating);
        for (var i = 0; i < fullStars; i++) {
            stars += '★';
        }
        for (var i = fullStars; i < 5; i++) {
            stars += '☆';
        }
        return stars;
    };
}]);


// =====================================================
// Admin Employers Controller
// =====================================================
app.controller('AdminEmployersController', ['$scope', '$http', '$location', '$window', function($scope, $http, $location, $window) {
    // Check if admin is logged in
    var admin = $window.localStorage.getItem('mlgms_admin');
    if (!admin) {
        $location.path('/admin-login');
        return;
    }
    
    $scope.employers = [];
    $scope.filteredEmployers = [];
    $scope.stats = {};
    $scope.filterStatus = 'pending';
    $scope.loading = true;
    $scope.showDetails = false;
    $scope.selectedEmployer = null;
    $scope.verificationNotes = '';
    
    // Load employers
    $scope.loadEmployers = function() {
        $scope.loading = true;
        
        $http.get(API_BASE_URL + '/admin/employers')
            .then(function(response) {
                if (response.data.success) {
                    $scope.employers = response.data.employers;
                    $scope.applyFilter();
                }
            })
            .catch(function(error) {
                console.error('Error loading employers:', error);
            })
            .finally(function() {
                $scope.loading = false;
            });
        
        // Load stats
        $http.get(API_BASE_URL + '/admin/stats')
            .then(function(response) {
                if (response.data.success) {
                    $scope.stats = response.data.stats.employers;
                }
            });
    };
    
    // Set filter
    $scope.setFilter = function(status) {
        $scope.filterStatus = status;
        $scope.applyFilter();
    };
    
    // Apply filter
    $scope.applyFilter = function() {
        if ($scope.filterStatus === 'all') {
            $scope.filteredEmployers = $scope.employers;
        } else {
            $scope.filteredEmployers = $scope.employers.filter(function(e) {
                return e.is_verified === $scope.filterStatus;
            });
        }
    };
    
    // View details
    $scope.viewDetails = function(employer) {
        $scope.selectedEmployer = employer;
        $scope.showDetails = true;
        $scope.verificationNotes = '';
    };
    
    // Verify employer
    $scope.verifyEmployer = function(employer) {
        $http.post(API_BASE_URL + '/admin/employers/' + employer.id + '/verify', {
            notes: $scope.verificationNotes
        })
            .then(function(response) {
                if (response.data.success) {
                    employer.is_verified = 'verified';
                    $scope.showDetails = false;
                    $scope.loadEmployers();
                }
            })
            .catch(function(error) {
                alert('Error verifying employer');
            });
    };
    
    // Reject employer
    $scope.rejectEmployer = function(employer) {
        if (!confirm('Are you sure you want to reject this employer?')) {
            return;
        }
        
        $http.post(API_BASE_URL + '/admin/employers/' + employer.id + '/reject', {
            notes: $scope.verificationNotes
        })
            .then(function(response) {
                if (response.data.success) {
                    employer.is_verified = 'rejected';
                    $scope.showDetails = false;
                    $scope.loadEmployers();
                }
            })
            .catch(function(error) {
                alert('Error rejecting employer');
            });
    };
    
    // Navigate
    $scope.navigateTo = function(path) {
        $location.path('/' + path);
    };
    
    // Initial load
    $scope.loadEmployers();
}]);


// =====================================================
// Uppercase Filter
// =====================================================
app.filter('uppercase', function() {
    return function(input) {
        return input ? input.toUpperCase() : '';
    };
});
