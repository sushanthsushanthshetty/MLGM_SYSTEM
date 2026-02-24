// Migrant Labor & Grievance Management System
// AngularJS Controllers

// Home Controller
app.controller('HomeController', ['$scope', function($scope) {
    $scope.projectTitle = 'Migrant Labor & Grievance Management System';
    $scope.description = 'A comprehensive government portal for migrant workers to register, manage profiles, file complaints, and connect with employers. This system aims to protect the rights of migrant workers and ensure their grievances are addressed promptly.';
}]);

// Register Controller
app.controller('RegisterController', ['$scope', function($scope) {
    // Initialize form data
    $scope.formData = {
        name: '',
        mobile: '',
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
    
    // Register function - validates form before submission
    $scope.register = function() {
        // Check if form is valid
        if ($scope.registerForm.$invalid) {
            // Mark all fields as touched to show validation errors
            $scope.registerForm.$setSubmitted();
            return;
        }
        
        // Form is valid, proceed with registration
        console.log('Registration data:', $scope.formData);
        $scope.registrationSuccess = true;
    };
    
    // Reset form
    $scope.resetForm = function() {
        $scope.formData = {
            name: '',
            mobile: '',
            age: '',
            gender: '',
            skill: ''
        };
        $scope.registrationSuccess = false;
        // Reset form validation state
        if ($scope.registerForm) {
            $scope.registerForm.$setPristine();
            $scope.registerForm.$setUntouched();
        }
    };
}]);

// Login Controller
app.controller('LoginController', ['$scope', '$location', function($scope, $location) {
    // Initialize login data
    $scope.loginData = {
        migrantId: '',
        mobile: ''
    };
    
    // Login function - navigate to dashboard
    $scope.login = function() {
        $location.path('/dashboard');
    };
}]);

// Dashboard Controller
app.controller('DashboardController', ['$scope', '$location', function($scope, $location) {
    // Dashboard menu items
    $scope.menuItems = [
        { title: 'My Profile', icon: '👤', link: '#!/profile', color: '#0d6efd' },
        { title: 'File Complaint', icon: '📝', link: '#!/complaint', color: '#dc3545' },
        { title: 'My Complaints', icon: '📋', link: '#!/complaints', color: '#ffc107' },
        { title: 'Employer List', icon: '🏢', link: '#!/employers', color: '#28a745' },
        { title: 'Logout', icon: '🚪', link: '#!/', color: '#6c757d' }
    ];
    
    // Navigate to page
    $scope.navigateTo = function(link) {
        $location.path(link.replace('#!/', ''));
    };
}]);

// Profile Controller
app.controller('ProfileController', ['$scope', function($scope) {
    // Dummy worker profile data
    $scope.worker = {
        name: 'Ramesh Kumar',
        migrantId: 'MID12345',
        skill: 'Electrician',
        mobile: '9876543210',
        age: 32,
        gender: 'Male',
        address: 'Village - Rampur, District - Agra, Uttar Pradesh',
        registrationDate: '15 January 2024',
        status: 'Active',
        currentEmployer: 'ABC Construction Pvt Ltd',
        workLocation: 'Mumbai, Maharashtra'
    };
}]);

// Complaint Controller
app.controller('ComplaintController', ['$scope', function($scope) {
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
    
    // Submission success flag
    $scope.submissionSuccess = false;
    
    // Submit complaint function - validates form before submission
    $scope.submitComplaint = function() {
        // Check if form is valid
        if ($scope.complaintForm.$invalid) {
            $scope.complaintForm.$setSubmitted();
            return;
        }
        
        // Form is valid, proceed with submission
        console.log('Complaint data:', $scope.complaintData);
        $scope.submissionSuccess = true;
    };
    
    // Reset form
    $scope.resetForm = function() {
        $scope.complaintData = {
            type: '',
            description: ''
        };
        $scope.submissionSuccess = false;
        // Reset form validation state
        if ($scope.complaintForm) {
            $scope.complaintForm.$setPristine();
            $scope.complaintForm.$setUntouched();
        }
    };
}]);

// Complaints List Controller
app.controller('ComplaintsController', ['$scope', function($scope) {
    // Dummy complaints list
    $scope.complaints = [
        { id: 'CMP001', type: 'Non-Payment of Wages', status: 'Pending', date: '2024-01-10' },
        { id: 'CMP002', type: 'Safety Issues', status: 'Resolved', date: '2024-01-05' },
        { id: 'CMP003', type: 'Workplace Harassment', status: 'Pending', date: '2024-01-12' },
        { id: 'CMP004', type: 'Contract Violation', status: 'Resolved', date: '2024-01-02' },
        { id: 'CMP005', type: 'Accommodation Problems', status: 'Pending', date: '2024-01-15' }
    ];
    
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

// Employers Controller
app.controller('EmployersController', ['$scope', function($scope) {
    // Dummy employers list
    $scope.employers = [
        { 
            name: 'ABC Construction Pvt Ltd', 
            rating: 4.5, 
            status: 'Active',
            location: 'Mumbai, Maharashtra',
            workers: 150,
            type: 'Construction'
        },
        { 
            name: 'XYZ Manufacturing Co', 
            rating: 4.0, 
            status: 'Active',
            location: 'Pune, Maharashtra',
            workers: 200,
            type: 'Manufacturing'
        },
        { 
            name: 'LMN Textiles', 
            rating: 3.5, 
            status: 'Inactive',
            location: 'Surat, Gujarat',
            workers: 80,
            type: 'Textile'
        },
        { 
            name: 'PQR Infrastructure', 
            rating: 4.8, 
            status: 'Active',
            location: 'Delhi NCR',
            workers: 300,
            type: 'Infrastructure'
        },
        { 
            name: 'EFG Hospitality Services', 
            rating: 4.2, 
            status: 'Active',
            location: 'Bangalore, Karnataka',
            workers: 120,
            type: 'Hospitality'
        },
        { 
            name: 'HIJ Agricultural Farms', 
            rating: 3.8, 
            status: 'Active',
            location: 'Nashik, Maharashtra',
            workers: 50,
            type: 'Agriculture'
        }
    ];
    
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