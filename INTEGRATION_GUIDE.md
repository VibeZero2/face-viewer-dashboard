# Face Perception Study - Dashboard Integration Guide

## Overview
This guide explains how the facial-trust-study (study program) and face-viewer-dashboard (analytics dashboard) work together on Render deployment.

## Data Flow Architecture

### 1. Study Program Data Collection
- **Location**: `facial-trust-study` repository
- **Data Storage**: `data/responses/` directory
- **File Format**: CSV files with timestamped filenames
- **Naming Convention**: `{prolific_pid}_{timestamp}.csv`

### 2. Dashboard Data Processing
- **Location**: `face-viewer-dashboard` repository  
- **Data Source**: Same `data/responses/` directory
- **Processing**: Standardizes column names and applies exclusion rules
- **Output**: Cleaned data for statistical analysis

## Data Structure Mapping

### Study Program CSV Format:
```csv
pid,timestamp,face_id,version,order_presented,trust_rating,masc_choice,fem_choice,trust_q1,trust_q2,trust_q3,pers_q1,pers_q2,pers_q3,pers_q4,pers_q5,prolific_pid
```

### Dashboard Standardized Format:
```csv
participant_id,timestamp,face_id,version,trial_order,trust_rating,masculinity_choice,femininity_choice,trust_question_1,trust_question_2,trust_question_3,personality_question_1,personality_question_2,personality_question_3,personality_question_4,personality_question_5,prolific_pid
```

## Column Mapping

| Study Program | Dashboard | Description |
|---------------|-----------|-------------|
| `pid` | `participant_id` | Participant identifier |
| `face_id` | `face_id` | Face image identifier |
| `version` | `version` | Trial type (left/right/full/toggle/survey) |
| `trust_rating` | `trust_rating` | Trustworthiness rating |
| `masc_choice` | `masculinity_choice` | Masculinity choice |
| `fem_choice` | `femininity_choice` | Femininity choice |
| `trust_q1-3` | `trust_question_1-3` | Trust questionnaire items |
| `pers_q1-5` | `personality_question_1-5` | Personality questionnaire items |
| `order_presented` | `trial_order` | Trial presentation order |

## Version Types

### Study Program Versions:
- `left`: Left half of face
- `right`: Right half of face  
- `full`: Full face
- `toggle`: Left/right toggle trial
- `survey`: Survey responses

### Dashboard Processing:
- Maps `left half` → `left`
- Maps `right half` → `right`
- Maps `full face` → `full`
- Preserves `toggle` and `survey` for analysis

## Render Deployment Strategy

### Option 1: Shared Volume (Recommended)
1. **Study Program**: Deploy to Render with persistent volume
2. **Dashboard**: Deploy to same Render service or linked service
3. **Shared Data**: Both access same `data/responses/` directory

### Option 2: Separate Services with Data Sync
1. **Study Program**: Deploy as web service
2. **Dashboard**: Deploy as separate web service
3. **Data Sync**: Use webhook or scheduled sync to copy data

### Option 3: Database Integration
1. **Study Program**: Save to database instead of CSV
2. **Dashboard**: Read from same database
3. **Advantage**: Better data integrity and querying

## Current Implementation Status

### ✅ Working:
- Data loading from multiple CSV formats
- Column name standardization
- Basic statistical analysis
- Dashboard UI with data management

### ⚠️ Needs Attention:
- Version mapping for study program data
- Survey data processing
- Trial order analysis
- Prolific ID integration

### 🔧 To Implement:
- Real-time data sync between services
- Database backend for production
- Data validation and error handling
- Backup and recovery procedures

## File Structure for Render

```
facial-trust-study/
├── app.py                 # Study program Flask app
├── data/
│   └── responses/         # Shared data directory
│       ├── {prolific_pid}_{timestamp}.csv
│       └── ...
└── static/
    └── images/           # Face images

face-viewer-dashboard/
├── dashboard_app.py       # Dashboard Flask app
├── analysis/             # Data processing modules
├── data/
│   └── responses/        # Same shared directory
└── templates/            # Dashboard UI
```

## Next Steps for Production

1. **Deploy Study Program** to Render
2. **Deploy Dashboard** to Render (same or linked service)
3. **Test Data Flow** with sample participants
4. **Configure Environment Variables** for production
5. **Set up Monitoring** and error tracking
6. **Implement Data Backup** procedures

## Environment Variables Needed

### Study Program:
```
FLASK_SECRET_KEY=your-secret-key
FERNET_KEY=your-encryption-key
```

### Dashboard:
```
DASHBOARD_SECRET_KEY=your-dashboard-secret
DATA_DIR=/path/to/shared/data
```

## Testing Integration

1. **Local Testing**: Run both services locally with shared data directory
2. **Render Testing**: Deploy both services and test data flow
3. **Data Validation**: Verify data integrity and processing
4. **Performance Testing**: Test with multiple concurrent participants
