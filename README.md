# Learning Platform 🎓

A comprehensive Django-based educational platform connecting teachers and students in an interactive learning environment with secure payment processing and course management capabilities.

## 🌟 Features

### Multi-Role Authentication
- **Teacher Registration**: Create courses, manage content, and track revenue
- **Student Registration**: Browse courses, make payments, and access learning materials
- **Email Verification**: OTP-based secure account verification system

### Course Management
- **Course Creation**: Rich course descriptions with category organization
- **Content Management**: Upload lessons, PDFs, videos, and other resources
- **Search & Filtering**: Advanced course discovery with category-based filtering
- **Progress Tracking**: Monitor student enrollment and learning progress

### Payment Processing
- **PayPal Integration**: Secure payment gateway with sandbox/live mode support
- **Transaction Management**: Real-time payment status tracking and verification
- **Revenue Analytics**: Comprehensive earning reports for instructors
- **Automated Enrollment**: Instant course access upon successful payment

### API & Integration
- **REST API**: Complete API endpoints for mobile and external integrations
- **Swagger Documentation**: Interactive API documentation and testing
- **CORS Support**: Cross-origin requests for frontend applications
- **Token Authentication**: Secure API access with multiple authentication methods

### Teacher Dashboard
- Course creation and management interface
- Student enrollment analytics
- Revenue tracking and reporting

### Student Dashboard  
- Course discovery and enrollment
- Payment processing workflow
- Learning progress tracking

### Payment Flow
- Secure PayPal checkout integration
- Real-time transaction verification
- Automatic course access provisioning

## 🏗️ Architecture

[9]

```
learning_platform/
├── accounts/                 # User management & authentication
│   ├── models.py            # Custom user model with roles
│   ├── views.py             # Registration, login, OTP verification
│   └── forms.py             # User registration forms
├── courses/                 # Course & content management
│   ├── models.py            # Course, content, subscription models
│   ├── views.py             # Course CRUD, dashboards
│   └── forms.py             # Course creation forms
├── payment_gateway/         # Payment processing
│   ├── models.py            # Payment transaction models
│   ├── views.py             # PayPal integration logic
│   └── services.py          # Payment service handlers
├── api/                     # REST API endpoints
│   ├── serializers/         # API data serialization
│   ├── views/              # API view controllers
│   └── urls.py             # API route configuration
├── templates/              # HTML templates
├── static/                # CSS, JS, images
└── media/                 # User uploaded files
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **pip** (Python package manager)
- **Git**

### Installation

1. **Clone Repository**:
   ```bash
   git clone https://github.com/m-gopinath03/learning_platform.git
   cd learning_platform
   ```

2. **Setup Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create `.env` file:
   ```env
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   PAYPAL_CLIENT_ID=your_paypal_client_id
   PAYPAL_CLIENT_SECRET=your_paypal_client_secret
   ```

4. **Setup Database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Launch Application**:
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000` to access the platform.

### First Steps

1. **Register as Teacher**: Create courses and upload content
2. **Register as Student**: Browse and enroll in courses
3. **Test Payments**: Use PayPal sandbox for payment testing
4. **Explore API**: Access Swagger docs at `/swagger/`

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Backend** | Django 5.0.1 | Web framework |
| **Database** | SQLite/PostgreSQL | Data persistence |
| **API** | Django REST Framework | API endpoints |
| **Authentication** | Django Auth + Custom User | User management |
| **Payments** | PayPal SDK | Secure transactions |
| **Frontend** | Bootstrap + jQuery | Responsive UI |
| **Email** | SMTP (Gmail) | OTP verification |
| **Documentation** | drf-yasg (Swagger) | API docs |
| **File Storage** | Django FileField | Media uploads |

## 🔧 Usage Examples

### Teacher Workflow
```python
# Create Course
POST /api/courses/
{
    "title": "Django Fundamentals",
    "description": "Learn Django web development",
    "price": 99.99,
    "category": 1
}

# Add Course Content
POST /courses/{slug}/add-content/
{
    "title": "Introduction to Django",
    "content": "Course materials...",
    "file": "lesson1.pdf"
}
```

### Student Workflow
```python
# Enroll in Course
POST /api/payments/process/{course_id}/

# Access Course Content
GET /api/courses/my-courses/
```

### Payment Processing
```python
# Initialize Payment
payment = Payment.objects.create(
    user=request.user,
    course=course,
    amount=course.price,
    status='pending'
)

# PayPal Integration
paypal_service = PayPalService()
order = paypal_service.create_order(payment)
```

## 📱 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/verify-otp/` - Email verification

### Courses
- `GET /api/courses/` - List courses
- `POST /api/courses/` - Create course
- `GET /api/courses/{id}/` - Course details
- `POST /api/courses/{id}/enroll/` - Course enrollment

### Payments
- `POST /api/payments/process/{course_id}/` - Initialize payment
- `GET /api/payments/verify/` - Payment verification
- `POST /api/payments/success/` - Payment success callback

## 🔒 Security Features

- **Role-Based Access**: Teacher/Student permission system
- **CSRF Protection**: Cross-site request forgery prevention  
- **OTP Verification**: Email-based account verification
- **Secure Payments**: PayPal SDK integration
- **File Validation**: Upload security and type checking

## 📊 Key Features Comparison

| Feature | Teachers | Students | API |
|---------|----------|----------|-----|
| **Course Management** | ✅ Create & Edit | ❌ View Only | ✅ Full CRUD |
| **Payment Processing** | ✅ Receive Payments | ✅ Make Payments | ✅ Transaction APIs |
| **Content Access** | ✅ All Courses | ✅ Enrolled Only | ✅ Permission-based |
| **Analytics** | ✅ Revenue Reports | ✅ Progress Tracking | ✅ Data Export |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Django** | [Issues](https://github.com/m-gopinath03/learning_platform/issues) | [Documentation](https://github.com/m-gopinath03/learning_platform/wiki)
