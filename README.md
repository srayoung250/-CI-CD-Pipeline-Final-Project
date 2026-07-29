# Mechanic Shop API - CI/CD Pipeline

A production-ready REST API for managing a mechanic shop with comprehensive CI/CD automation using GitHub Actions and Render deployment.

## 🚀 Features

- **Full REST API** for managing customers, mechanics, service tickets, and inventory
- **JWT Authentication** for secure access
- **Rate Limiting & Caching** for performance optimization
- **Interactive Swagger/OpenAPI Documentation** with full test capabilities
- **Automated CI/CD Pipeline** with GitHub Actions
- **Automated Deployment** to Render on every push to main branch
- **PostgreSQL Database** for reliable data persistence
- **Comprehensive Test Suite** with pytest
- **Production-ready** with gunicorn WSGI server

## 📋 Project Structure

```
.
├── .github/
│   └── workflows/
│       └── main.yaml                 # GitHub Actions CI/CD workflow
├── app/
│   ├── blueprints/
│   │   ├── customer/                # Customer management endpoints
│   │   ├── mechanic/                # Mechanic management endpoints
│   │   ├── service_ticket/          # Service ticket management endpoints
│   │   └── inventory/               # Inventory management endpoints
│   ├── __init__.py                  # Flask app factory
│   ├── extensions.py                # Flask extensions (SQLAlchemy, etc.)
│   ├── models.py                    # Database models
│   ├── swagger_definitions.py       # API documentation definitions
│   └── utils.py                     # Utility functions
├── tests/
│   ├── base.py                      # Test configuration
│   ├── test_customers.py            # Customer endpoint tests
│   ├── test_mechanics.py            # Mechanic endpoint tests
│   ├── test_inventory.py            # Inventory endpoint tests
│   └── test_service_tickets.py      # Service ticket endpoint tests
├── config.py                        # Flask configuration (Dev/Test/Prod)
├── flask_app.py                     # Application entry point
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (local development)
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

## 🛠️ Tech Stack

- **Backend:** Flask 3.1.3
- **Database:** PostgreSQL (Render-hosted)
- **ORM:** SQLAlchemy 2.0
- **Serialization:** Marshmallow
- **Authentication:** JWT (python-jose)
- **API Documentation:** Flasgger (Swagger/OpenAPI)
- **Rate Limiting:** Flask-Limiter
- **Caching:** Flask-Caching
- **Production Server:** Gunicorn
- **Testing:** pytest
- **CI/CD:** GitHub Actions
- **Hosting:** Render

## 📦 Prerequisites

- Python 3.9+
- PostgreSQL database (or use Render's managed PostgreSQL)
- Git & GitHub account
- Render account (for deployment)

## 🔧 Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/srayoung250/-CI-CD-Pipeline-Final-Project.git
cd mechanic-api-ci-cd-pipeline
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```env
FLASK_ENV=development
DATABASE_URI=sqlite:///mechanic_shop.db
SECRET_KEY=your-development-secret-key-here
```

**For production** (on Render), set these in the Render dashboard:
```env
FLASK_ENV=production
DATABASE_URI=postgresql://user:password@host:5432/mechanic_shop
SECRET_KEY=your-production-secret-key-here
```

### 5. Run the Application
```bash
python flask_app.py
```

The API will be available at `http://localhost:5000`

## 📖 API Documentation

Once the application is running, visit:
```
http://localhost:5000/apidocs
```

This opens the interactive Swagger UI where you can:
- View all available endpoints
- Test endpoints directly
- See request/response schemas
- Try different HTTP methods (GET, POST, PUT, DELETE)

## 🔑 API Endpoints

### Customers
- `GET /customers` - List all customers
- `GET /customers/<id>` - Get customer by ID
- `POST /customers` - Create new customer
- `PUT /customers/<id>` - Update customer
- `DELETE /customers/<id>` - Delete customer

### Mechanics
- `GET /mechanics` - List all mechanics
- `GET /mechanics/<id>` - Get mechanic by ID
- `POST /mechanics` - Create new mechanic
- `PUT /mechanics/<id>` - Update mechanic
- `DELETE /mechanics/<id>` - Delete mechanic

### Service Tickets
- `GET /service-tickets` - List all service tickets
- `GET /service-tickets/<id>` - Get service ticket by ID
- `POST /service-tickets` - Create new service ticket
- `PUT /service-tickets/<id>` - Update service ticket
- `DELETE /service-tickets/<id>` - Delete service ticket

### Inventory
- `GET /inventory` - List all inventory items
- `GET /inventory/<id>` - Get inventory item by ID
- `POST /inventory` - Create new inventory item
- `PUT /inventory/<id>` - Update inventory item
- `DELETE /inventory/<id>` - Delete inventory item

## 🧪 Testing

Run the test suite locally:
```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=html
```

Tests are automatically run by GitHub Actions on every push and pull request.

## 🚀 Deployment

### Production Deployment (Render)

The application is deployed on Render at:
```
https://mechanic-shop-api-o2l5.onrender.com
```

**Live API Documentation:**
```
https://mechanic-shop-api-o2l5.onrender.com/apidocs
```

### Deployment Process

1. **Database Setup:**
   - PostgreSQL database is hosted on Render
   - Tables are automatically created on app startup

2. **Environment Configuration:**
   - Environment variables are stored securely in Render dashboard
   - No sensitive data is committed to git

3. **Auto-Deployment:**
   - Any push to the `main` branch triggers automatic deployment
   - GitHub Actions runs tests before deploying
   - Deployment only proceeds if all tests pass

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

Located in `.github/workflows/main.yaml`, the pipeline includes:

#### 1. **Build Job**
- Installs Python dependencies
- Verifies all packages are available

#### 2. **Test Job** (depends on Build)
- Runs pytest test suite
- Generates code coverage report
- Uploads coverage to Codecov

#### 3. **Deploy Job** (depends on Test)
- Only runs on pushes to main branch
- Calls Render API to trigger deployment
- Requires GitHub secrets: `RENDER_SERVICE_ID` and `RENDER_API_KEY`

### Workflow Triggers

- **Automatic:** Push to `main` branch
- **Automatic:** Pull requests to `main` branch
- **Manual:** Can be triggered from GitHub Actions tab

### View Workflow Status

```
https://github.com/srayoung250/-CI-CD-Pipeline-Final-Project/actions
```

## 🔐 Environment Variables & Secrets

### Local Development (`.env` file)
```env
FLASK_ENV=development
DATABASE_URI=sqlite:///mechanic_shop.db
SECRET_KEY=dev-secret-key
```

### Production (Render Dashboard)
```env
FLASK_ENV=production
DATABASE_URI=postgresql://user:password@host:5432/mechanic_shop
SECRET_KEY=<securely-generated-key>
```

### GitHub Secrets (for CI/CD)
- `RENDER_SERVICE_ID` - Your Render service ID
- `RENDER_API_KEY` - Your Render API key

## 🛠️ Configuration

The application supports three environments via `config.py`:

### Development Config
- `DEBUG=True`
- SQLite database
- Simplified error handling

### Testing Config
- `TESTING=True`
- In-memory SQLite database
- Optimized for fast test execution

### Production Config
- `DEBUG=False`
- PostgreSQL database
- Enhanced security settings

## 📚 Key Technologies

### Flask & Extensions
- **Flask-SQLAlchemy:** ORM for database operations
- **flask-marshmallow:** JSON serialization/deserialization
- **Flasgger:** Swagger API documentation
- **Flask-Limiter:** Rate limiting
- **Flask-Caching:** Response caching

### Database
- **SQLAlchemy:** SQL toolkit and ORM
- **psycopg2:** PostgreSQL adapter
- **Alembic:** Database migrations (future)

### Security & Authentication
- **python-jose:** JWT token handling
- **python-dotenv:** Environment variable management

### Testing
- **pytest:** Testing framework
- **pytest-cov:** Code coverage

## 🐛 Troubleshooting

### 500 Internal Server Error

**Check Render Logs:**
1. Go to Render dashboard
2. Select your service
3. Click "Logs" tab
4. Look for error messages

**Common Issues:**
- Database connection error → Verify `DATABASE_URI` environment variable
- Missing tables → Tables auto-create on app startup
- Import errors → Check Python path and dependencies

### Tests Failing

Run tests locally to debug:
```bash
pytest tests/ -v -s
```

Check test output for specific failures and fix accordingly.

### Deployment Not Triggering

- Ensure you pushed to the `main` branch
- Check GitHub Actions workflow status
- Verify GitHub secrets are set correctly

## 📝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest tests/ -v`
4. Commit: `git commit -m "Add your feature"`
5. Push: `git push origin feature/your-feature`
6. Create a Pull Request

All PRs trigger the CI/CD pipeline and require passing tests to merge.

## 📄 License

This project is part of the Mechanic Shop API course curriculum.

## 👨‍💻 Author

- **GitHub:** [@srayoung250](https://github.com/srayoung250)
- **Email:** srayoung250@gmail.com

## 🎯 Project Status

✅ **Production Ready**
- Full CI/CD pipeline operational
- Automated testing on every commit
- Automated deployment to Render
- Database auto-initialization
- Swagger documentation live

## 📞 Support

For issues, questions, or suggestions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the [Render deployment guide](DEPLOYMENT_GUIDE.md)
3. Check GitHub Actions logs for CI/CD issues
4. Refer to Flask documentation: https://flask.palletsprojects.com/
5. Refer to Render documentation: https://render.com/docs/

## 🚀 Next Steps

- Add database migrations with Alembic
- Implement more sophisticated error handling
- Add request validation
- Implement user authentication dashboard
- Add batch operations support
- Performance optimization with caching strategies

---

**Live API:** https://mechanic-shop-api-o2l5.onrender.com  
**API Docs:** https://mechanic-shop-api-o2l5.onrender.com/apidocs  
**GitHub:** https://github.com/srayoung250/-CI-CD-Pipeline-Final-Project
