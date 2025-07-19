# Face Viewer Dashboard

A secure dashboard application for the Face Half Viewer study, providing data visualization, analysis, and management capabilities.

## Features

- **Secure Authentication**: Login-protected dashboard for administrators only
- **Data Visualization**: Interactive Plotly charts showing trust ratings and other metrics
- **Statistical Analysis**: Integration with R for mixed-effects modeling and advanced statistics
- **Data Management**: Download individual participant data or bulk download all data
- **Session Management**: Monitor and manage abandoned sessions
- **Dark Theme**: Matches the styling of the Face Half Viewer and Face Analysis Tool applications

## Setup

### Prerequisites

- Python 3.8+
- R (optional, for statistical analysis features)
- Face Half Viewer Web application data directory

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```
   FLASK_SECRET_KEY=your_secret_key
   DASHBOARD_SECRET_KEY=your_dashboard_secret_key
   FERNET_KEY=same_key_as_face_viewer_app
   FACE_VIEWER_DATA_DIR=/path/to/face_viewer_data
   ```

### Running the Dashboard

```bash
python app.py
```

The dashboard will be available at http://localhost:5001 by default.

## Environment Variables

- `FLASK_SECRET_KEY`: Secret key for Flask session security
- `DASHBOARD_SECRET_KEY`: Secret key for dashboard authentication
- `FERNET_KEY`: Encryption key (must match the key used by Face Half Viewer app)
- `FACE_VIEWER_DATA_DIR`: Path to the Face Half Viewer data directory

## Usage

1. **Login**: Access the dashboard using admin credentials
2. **Dashboard Overview**: View summary statistics and visualizations
3. **Participant Details**: Click on a participant ID to view detailed data
4. **R Analysis**: Access statistical analysis and model results
5. **Data Download**: Download individual or bulk participant data
6. **Check Abandoned Sessions**: Manually trigger checks for abandoned sessions

## Integration with Face Half Viewer

This dashboard reads data files from the Face Half Viewer application's data directory. It uses the same Fernet encryption key to decrypt the data files.

## Security

- All routes are protected by Flask-Login authentication
- Participant data is encrypted at rest
- API endpoints require authentication
- Password hashing for user credentials

## Development

To run the dashboard in development mode:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```
