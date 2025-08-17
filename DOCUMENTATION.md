# Face Viewer Dashboard Documentation

## Overview
This documentation provides information about the Face Viewer Dashboard application, its components, and how to run it locally for development and testing.

## Application Structure

### Main Components
- **Flask Application**: The main web application framework
- **Blueprints**: Modular components for different parts of the application
  - `admin_bp`: Admin authentication and tools
  - `dashboard_bp`: Main dashboard display
  - `analytics_bp`: Analytics and data analysis features
- **Authentication**: Custom session-based authentication via `AdminAuth` class

### Key Files
- **App Entry Points**:
  - `simple.py`: Simplified version for local testing
  - `app_dashboard_integration.py`: Full version with dashboard integration
  - `app_no_pandas.py`: Version without pandas dependency
  - `wsgi.py`: WSGI entry point for production
- **Routes**:
  - `routes/dashboard.py`: Dashboard routes
  - `routes/analytics_no_pandas.py`: Analytics routes without pandas
  - `routes/admin_tools.py`: Admin tools and authentication routes
- **Templates**:
  - `templates/base.html`: Base template with common layout
  - `templates/dashboard.html`: Main dashboard template
  - `templates/analytics/dashboard.html`: Analytics dashboard template
  - `templates/admin/*.html`: Admin templates

## Local Development

### Setup
1. Create a Python virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create required directories and files:
   ```
   mkdir -p data/responses
   mkdir -p data/admin
   ```

4. Create admin users file (`data/admin/admin_users.json`):
   ```json
   {
     "users": [
       {
         "username": "admin",
         "password_hash": "pbkdf2:sha256:150000$KCncc9d1$a4c9b5d3a1e0b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2",
         "role": "admin"
       }
     ]
   }
   ```
   (Default password is "password")

5. Generate test data:
   ```
   python create_test_data_simple.py
   ```

### Running Locally
1. Run the simple version for local testing:
   ```
   python simple.py
   ```
   or
   ```
   python run_debug.py
   ```

2. Access the application:
   - Main URL: http://localhost:5000
   - Dashboard: http://localhost:5000/dashboard
   - Analytics: http://localhost:5000/analytics
   - Admin Login: http://localhost:5000/admin/login

### Authentication
- Login is required for accessing dashboard and analytics pages
- Default credentials:
  - Username: admin
  - Password: password

## Data Structure

### Participant Data
- Stored in CSV files in `data/responses/` directory
- Each participant has their own CSV file
- Key fields:
  - `ParticipantID`: Unique identifier
  - `Timestamp`: When the response was recorded
  - `FaceVersion`: Type of face shown (Full Face, Left Half, Right Half)
  - `TrustRating`: Trust rating score
  - `MasculinityRating`: Masculinity rating score
  - `FemininityRating`: Femininity rating score
  - `SymmetryRating`: Symmetry rating score

## Analytics Features

### Available Analyses
1. **Descriptive Statistics**:
   - Mean, median, min, max, standard deviation
   - Available for any numeric variable

2. **T-Test**:
   - Compares means between Left Half and Right Half face versions
   - Shows count, mean, and standard deviation for each group

3. **Correlation Analysis**:
   - Basic correlation between two selected variables
   - Note: Full correlation analysis requires scipy/numpy libraries

## Troubleshooting

### Common Issues
1. **Login Error**: If you see "NoneType object has no attribute 'authenticate'", ensure:
   - `data/admin/admin_users.json` exists with proper format
   - AdminAuth is properly initialized in the app

2. **No Data in Dropdowns**: If analytics dropdowns are empty:
   - Check that `data/responses/` directory contains CSV files
   - Run `create_test_data_simple.py` to generate test data

3. **Charts Not Displaying**: If dashboard charts are not showing:
   - Check browser console for JavaScript errors
   - Verify that data is being loaded correctly from the backend

## Deployment
The application can be deployed to platforms like Render or Netlify using the provided configuration files:
- `render.yaml`: Configuration for Render deployment
- `netlify.toml`: Configuration for Netlify deployment
- `Procfile`: For Heroku-compatible platforms
- `Dockerfile`: For container-based deployments

## Future Improvements
- Add full statistical analysis with scipy/numpy
- Implement user management features
- Add data visualization enhancements
- Improve mobile responsiveness
