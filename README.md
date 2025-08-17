# Face Viewer Dashboard

A secure dashboard application for the Face Half Viewer study, providing data visualization, analysis, and management capabilities. This dashboard integrates with the Face Half Viewer and Face Analysis Tool to provide comprehensive analysis of facial perception study data.

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

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check if port 5000/5001 is already in use
   - Verify Python version compatibility (3.8+ required)
   - Ensure all dependencies are installed correctly

2. **Charts not displaying**
   - Verify data files exist in the specified data directory
   - Check browser console for JavaScript errors
   - Ensure Plotly.js is loading correctly

3. **R Integration Issues**
   - Verify R is installed and accessible in PATH
   - Check that required R packages are installed
   - Look for error messages in the Flask logs

### Windows-Specific Setup

On Windows, use the provided batch files to start the server:

```batch
.\run_dashboard_server.bat
```

## Contributing

Contributions to the Face Viewer Dashboard are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure your code follows the existing style and includes appropriate tests.

## About

### Research Context

This dashboard was developed to support research investigating the question: **Does lateral asymmetry in masculine versus feminine facial features create distinctive patterns of implicit trust bias compared to viewing the whole face?**

The dashboard integrates with two companion applications:

1. **Face Half Viewer**
   - Displays split face views with center line
   - Supports both masculinity/femininity and trust perception testing modes
   - Calculates facial metrics (symmetry score, face ratio, quality score)
   - Saves participant responses with timestamps
   - Creates separate CSV files for each test type

2. **Face Analysis Tool**
   - Provides enhanced face analysis with masculinity scoring
   - Features split screen display showing both full face and split face views
   - Supports loading images from files or Word documents
   - Offers individual or batch CSV export options
   - Includes left/right side labeling and masculinity/femininity scoring

### Study Design Integration

The dashboard supports two primary study groups:

1. **Full Face Trust Perception Group**
   - Participants view and rate full faces for trustworthiness
   - Uses Likert scale 1-7
   - Collects optional explanations for ratings

2. **Split Face Analysis Group**
   - Participants rate left/right sides separately
   - Then view and rate the full face
   - System tracks changes in perception
   - Uses Likert scale 1-7

This dashboard provides visualization and analysis of the collected data, helping researchers identify patterns in how facial asymmetry affects trust perception.
