import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCleaner:
    """
    Data cleaning and exclusion logic for face perception study data.
    """
    
    def __init__(self, data_dir: str = "data/responses", test_mode: bool = False):
        self.data_dir = Path(data_dir)
        self.test_mode = test_mode
        self.raw_data = None
        self.cleaned_data = None
        self.exclusion_summary = {}
        
    def load_data(self) -> pd.DataFrame:
        """
        Load and merge CSV files from the responses directory.
        By default, only loads real study data files (participant_*.csv and study program files).
        Set test_mode=True to include test files.
        """
        csv_files = list(self.data_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {self.data_dir}")
        
        # Filter files based on mode
        if self.test_mode:
            # Test mode: include all files
            filtered_files = csv_files
            logger.info("TEST MODE: Loading all CSV files including test data")
        else:
            # Production mode: include real study data and study program files
            # Study program files: timestamped files (e.g., test789_20250725_123758.csv)
            # Real participant files: participant_*.csv
            # Prolific files: PROLIFIC_*.csv
            filtered_files = []
            excluded_files = []
            
            for file_path in csv_files:
                file_name = file_path.name
                
                # Exclude test files first (regardless of other patterns)
                if (file_name.startswith('test_') or 
                    file_name.startswith('test_participant') or
                    'test_statistical_validation' in file_name or
                    file_name.startswith('PROLIFIC_TEST_') or
                    file_name == 'test789.csv' or
                    file_name == 'test123.csv' or
                    file_name == 'test456.csv'):
                    excluded_files.append(file_name)
                    continue
                
                # Include real participant files
                if file_name.startswith('participant_'):
                    filtered_files.append(file_path)
                # Include study program files (timestamped files that are NOT test files)
                elif '_2025' in file_name and not file_name.startswith('test_'):
                    filtered_files.append(file_path)
                # Include other files that look like real study data
                elif not file_name.startswith('test_'):
                    filtered_files.append(file_path)
                else:
                    excluded_files.append(file_name)
            
            if excluded_files:
                logger.info(f"PRODUCTION MODE: Excluded test files: {excluded_files}")
            
            if not filtered_files:
                raise FileNotFoundError(f"No real study data files found in {self.data_dir}")
        
        all_data = []
        real_participants = 0
        total_rows = 0
        
        for file_path in filtered_files:
            try:
                df = pd.read_csv(file_path)
                
                # Add file metadata
                df['source_file'] = file_path.name
                df['loaded_at'] = pd.Timestamp.now()
                
                # Standardize column names - but preserve original names for mapping
                original_columns = df.columns.copy()
                df.columns = df.columns.str.lower().str.replace(' ', '_')
                
                all_data.append(df)
                
                # Count real participants (files that look like real data)
                if (file_path.name.startswith('participant_') or 
                    ('_2025' in file_path.name and not file_path.name.startswith('test_'))):
                    real_participants += 1
                
                total_rows += len(df)
                logger.info(f"Loaded {len(df)} rows from {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                continue
        
        if not all_data:
            raise ValueError("No valid CSV files could be loaded")
        
        # Merge all dataframes
        self.raw_data = pd.concat(all_data, ignore_index=True)
        
        # Log summary
        if self.test_mode:
            logger.info(f"TEST MODE: Total data loaded: {len(self.raw_data)} rows from {len(filtered_files)} files")
        else:
            logger.info(f"PRODUCTION MODE: Loaded {len(self.raw_data)} rows from {real_participants} real participants")
        
        return self.raw_data
    
    def get_data_summary(self) -> Dict:
        """
        Get summary of currently loaded data.
        """
        if self.raw_data is None:
            return {"status": "No data loaded"}
        
        # Count real participants (including study program files)
        real_files = []
        test_files = []
        
        for file_name in self.raw_data['source_file'].unique():
            if (file_name.startswith('participant_') or 
                ('_2025' in file_name and not file_name.startswith('test_'))):
                real_files.append(file_name)
            else:
                test_files.append(file_name)
        
        return {
            "mode": "TEST" if self.test_mode else "PRODUCTION",
            "total_rows": len(self.raw_data),
            "real_participants": len(real_files),
            "test_files": len(test_files),
            "real_files": real_files,
            "test_files_list": test_files
        }
    
    def standardize_data(self) -> pd.DataFrame:
        """
        Standardize data format across different CSV structures.
        """
        if self.raw_data is None:
            self.load_data()
        
        df = self.raw_data.copy()
        
        # Handle different column naming conventions
        # Map all data to study program format (pid, face_id, version, trust_rating)
        column_mapping = {
            # Study program uses these exact names - keep them
            'pid': 'pid',
            'face_id': 'face_id', 
            'version': 'version',
            'trust_rating': 'trust_rating',
            'timestamp': 'timestamp',
            'prolific_pid': 'prolific_pid',
            'order_presented': 'order_presented',
            # Map old format to study program format
            'participant_id': 'pid',
            'participantid': 'pid',
            'facenumber': 'face_id',  # Old format uses facenumber
            'face': 'face_id',
            'faceid': 'face_id',
            'faceversion': 'version',  # Old format uses faceversion
            'trust': 'trust_rating',   # Old format uses trust
            'emotion': 'emotion_rating',
            'masculinity': 'masculinity_rating',
            'femininity': 'femininity_rating',
            'symmetry': 'symmetry_rating',
            # Study program specific mappings
            'masc_choice': 'masc_choice',
            'fem_choice': 'fem_choice',
            'trust_q1': 'trust_q1',
            'trust_q2': 'trust_q2', 
            'trust_q3': 'trust_q3',
            'pers_q1': 'pers_q1',
            'pers_q2': 'pers_q2',
            'pers_q3': 'pers_q3',
            'pers_q4': 'pers_q4',
            'pers_q5': 'pers_q5'
        }
        
        # Rename columns that exist, handling duplicates
        existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        logger.info(f"Mapping columns: {existing_cols}")
        
        # Now rename the columns
        df = df.rename(columns=existing_cols)
        
        # Handle duplicate column names by keeping the first occurrence
        if df.columns.duplicated().any():
            logger.info("Handling duplicate columns by keeping first occurrence")
            # Use pandas built-in method to remove duplicates
            df = df.loc[:, ~df.columns.duplicated()]
            logger.info("Removed duplicate columns")
        
        # Ensure pid exists and has data (study program uses 'pid')
        if 'participant_id' in df.columns and 'pid' in df.columns:
            # Copy participant_id data to pid if pid is empty
            if df['pid'].isna().all():
                df['pid'] = df['participant_id']
                logger.info("Copied participant_id data to empty pid column")
            # Drop the participant_id column since we have pid
            df = df.drop(columns=['participant_id'])
            logger.info("Dropped participant_id column after ensuring pid has data")
        
        # Handle face_id conversion for study program format
        if 'face_id' in df.columns:
            # Study program uses 'face_1', 'face_2', etc.
            # Old format uses numbers like 1, 2, 3
            # Convert numeric face IDs to study program format
            if df['face_id'].dtype in ['int64', 'float64']:
                # Handle NaN values by filling them first
                df['face_id'] = df['face_id'].fillna('unknown')
                # Convert only non-NaN values
                numeric_mask = df['face_id'].notna() & (df['face_id'] != 'unknown')
                df.loc[numeric_mask, 'face_id'] = 'face_' + df.loc[numeric_mask, 'face_id'].astype(int).astype(str)
                logger.info("Converted numeric face_id to study program format (face_1, face_2, etc.)")
            elif df['face_id'].dtype == 'object':
                # Check if we have mixed formats
                numeric_faces = df['face_id'].str.match(r'^\d+$', na=False)
                if numeric_faces.any():
                    df.loc[numeric_faces, 'face_id'] = 'face_' + df.loc[numeric_faces, 'face_id'].astype(str)
                    logger.info("Converted numeric face_id values to study program format")
        
        # Ensure face_id exists and has data (study program uses 'face_id')
        if 'facenumber' in df.columns and 'face_id' in df.columns:
            # Copy facenumber data to face_id if face_id is empty
            if df['face_id'].isna().all():
                df['face_id'] = 'face_' + df['facenumber'].astype(str)
                logger.info("Copied facenumber data to empty face_id column")
            # Drop the facenumber column since we have face_id
            df = df.drop(columns=['facenumber'])
            logger.info("Dropped facenumber column after ensuring face_id has data")
        
        # Ensure version exists and has data (study program uses 'version')
        if 'faceversion' in df.columns and 'version' in df.columns:
            # Copy faceversion data to version if version is empty
            if df['version'].isna().all():
                df['version'] = df['faceversion']
                logger.info("Copied faceversion data to empty version column")
            # Drop the faceversion column since we have version
            df = df.drop(columns=['faceversion'])
            logger.info("Dropped faceversion column after ensuring version has data")
        
        # Ensure trust_rating exists and has data (study program uses 'trust_rating')
        if 'trust' in df.columns and 'trust_rating' in df.columns:
            # Copy trust data to trust_rating if trust_rating is empty
            if df['trust_rating'].isna().all():
                df['trust_rating'] = df['trust']
                logger.info("Copied trust data to empty trust_rating column")
            # Drop the trust column since we have trust_rating
            df = df.drop(columns=['trust'])
            logger.info("Dropped trust column after ensuring trust_rating has data")
        

        
        # Ensure required columns exist (study program uses these exact names)
        required_cols = ['pid', 'face_id', 'version', 'trust_rating']
        
        missing_cols = []
        for col in required_cols:
            if col not in df.columns:
                missing_cols.append(col)
        
        if missing_cols:
            logger.warning(f"Missing required columns: {missing_cols}")
            # Add missing columns with default values
            for col in missing_cols:
                df[col] = None
        
        # Standardize version values and filter out toggle/survey rows
        if 'version' in df.columns:
            # Convert to string first, then apply string operations
            df['version'] = df['version'].astype(str).str.lower().str.strip()
            version_mapping = {
                'left half': 'left',
                'right half': 'right',
                'full face': 'full',
                'left': 'left',
                'right': 'right',
                'full': 'full',
                'Left Half': 'left',
                'Right Half': 'right', 
                'Full Face': 'full'
            }
            df['version'] = df['version'].map(version_mapping).fillna(df['version'])
            
            # Filter out toggle and survey rows (ignore for now as requested)
            df = df[~df['version'].isin(['toggle', 'survey'])]
            logger.info(f"Filtered out toggle/survey rows. Remaining rows: {len(df)}")
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Convert ratings to numeric (study program uses 'trust_rating')
        rating_cols = ['trust_rating', 'emotion_rating', 'masculinity_rating', 'femininity_rating', 'symmetry_rating']
        for col in rating_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        self.raw_data = df
        return df
    
    def apply_exclusion_rules(self) -> pd.DataFrame:
        """
        Apply exclusion rules to create cleaned dataset.
        """
        if self.raw_data is None:
            self.standardize_data()
        
        df = self.raw_data.copy()
        
        # Initialize exclusion flags
        df['excl_failed_attention'] = False
        df['excl_fast_rt'] = False
        df['excl_slow_rt'] = False
        df['excl_device_violation'] = False
        df['include_in_primary'] = True
        
        # Session-level exclusions
        session_exclusions = self._apply_session_exclusions(df)
        df = session_exclusions['data']
        
        # Trial-level exclusions
        trial_exclusions = self._apply_trial_exclusions(df)
        df = trial_exclusions['data']
        
        # Combine exclusion summaries
        self.exclusion_summary = {
            'session_level': session_exclusions['summary'],
            'trial_level': trial_exclusions['summary'],
            'total_raw': len(self.raw_data),
            'total_cleaned': len(df[df['include_in_primary']])
        }
        
        self.cleaned_data = df
        return df
    
    def _apply_session_exclusions(self, df: pd.DataFrame) -> Dict:
        """
        Apply session-level exclusion rules.
        """
        summary = {
            'total_sessions': df['pid'].nunique(),
            'excluded_sessions': 0,
            'exclusion_reasons': {}
        }
        
        # Get unique participants
        participants = df['pid'].unique()
        
        for participant in participants:
            participant_data = df[df['pid'] == participant]
            
            # Check for attention check failures (placeholder - adjust based on your data)
            # This would need to be customized based on your actual attention check implementation
            attention_failed = False  # Placeholder
            
            # Check for device violations (placeholder)
            device_violation = False  # Placeholder
            
            # Check for duplicate prolific_pid (keep most complete session)
            if 'prolific_pid' in df.columns:
                prolific_pids = participant_data['prolific_pid'].dropna().unique()
                if len(prolific_pids) > 1:
                    # Keep session with most trials
                    session_completeness = participant_data.groupby('prolific_pid').size()
                    keep_pid = session_completeness.idxmax()
                    df.loc[df['prolific_pid'] != keep_pid, 'include_in_primary'] = False
            
            # Check for minimum trial completion (> 50% of expected trials for test data)
            # For real study data, this should be 60 trials, but for test data we're more lenient
            expected_trials = 60  # Adjust based on your study design
            actual_trials = len(participant_data)
            completion_rate = actual_trials / expected_trials
            
            # For test data, be more lenient (50% instead of 80%)
            # But only if it's actually test data (not real participant data)
            is_test_data = any(test_pattern in str(participant) for test_pattern in ['test_', 'test123', 'test456', 'test789'])
            min_completion_rate = 0.5 if (actual_trials < 48 and is_test_data) else 0.8  # 48 = 80% of 60
            
            if completion_rate < min_completion_rate:
                df.loc[df['pid'] == participant, 'include_in_primary'] = False
                summary['exclusion_reasons']['low_completion'] = summary['exclusion_reasons'].get('low_completion', 0) + 1
            
            if attention_failed:
                df.loc[df['pid'] == participant, 'excl_failed_attention'] = True
                df.loc[df['pid'] == participant, 'include_in_primary'] = False
                summary['exclusion_reasons']['attention_failed'] = summary['exclusion_reasons'].get('attention_failed', 0) + 1
            
            if device_violation:
                df.loc[df['pid'] == participant, 'excl_device_violation'] = True
                df.loc[df['pid'] == participant, 'include_in_primary'] = False
                summary['exclusion_reasons']['device_violation'] = summary['exclusion_reasons'].get('device_violation', 0) + 1
        
        summary['excluded_sessions'] = len(participants) - df[df['include_in_primary']]['pid'].nunique()
        
        return {'data': df, 'summary': summary}
    
    def _apply_trial_exclusions(self, df: pd.DataFrame) -> Dict:
        """
        Apply trial-level exclusion rules.
        """
        summary = {
            'total_trials': len(df),
            'excluded_trials': 0,
            'exclusion_reasons': {}
        }
        
        # Drop trials with RT < 200ms (if RT data available)
        if 'reaction_time' in df.columns:
            fast_trials = df['reaction_time'] < 200
            df.loc[fast_trials, 'excl_fast_rt'] = True
            df.loc[fast_trials, 'include_in_primary'] = False
            summary['exclusion_reasons']['fast_rt'] = fast_trials.sum()
        
        # Drop RTs > 99.5 percentile within subject (if RT data available)
        if 'reaction_time' in df.columns:
            for participant in df['pid'].unique():
                participant_data = df[df['pid'] == participant]
                rt_threshold = participant_data['reaction_time'].quantile(0.995)
                slow_trials = (df['pid'] == participant) & (df['reaction_time'] > rt_threshold)
                df.loc[slow_trials, 'excl_slow_rt'] = True
                df.loc[slow_trials, 'include_in_primary'] = False
                summary['exclusion_reasons']['slow_rt'] = summary['exclusion_reasons'].get('slow_rt', 0) + slow_trials.sum()
        
        summary['excluded_trials'] = len(df) - df['include_in_primary'].sum()
        
        return {'data': df, 'summary': summary}
    
    def get_cleaned_data(self) -> pd.DataFrame:
        """
        Get the cleaned dataset with exclusion flags.
        """
        if self.cleaned_data is None:
            self.apply_exclusion_rules()
        
        return self.cleaned_data
    
    def get_exclusion_summary(self) -> Dict:
        """
        Get summary of exclusion rules applied.
        """
        if self.exclusion_summary == {}:
            self.apply_exclusion_rules()
        
        return self.exclusion_summary
    
    def get_data_by_version(self, version: str) -> pd.DataFrame:
        """
        Get data filtered by face version (left, right, full).
        """
        cleaned_data = self.get_cleaned_data()
        return cleaned_data[
            (cleaned_data['version'] == version) & 
            (cleaned_data['include_in_primary'])
        ]
    
    def get_participant_summary(self) -> pd.DataFrame:
        """
        Get summary statistics per participant.
        """
        cleaned_data = self.get_cleaned_data()
        participant_data = cleaned_data[cleaned_data['include_in_primary']]
        
        summary = participant_data.groupby('pid').agg({
            'trust_rating': ['count', 'mean', 'std'],
            'version': 'nunique',
            'face_id': 'nunique'
        }).round(3)
        
        summary.columns = ['total_trials', 'mean_trust', 'std_trust', 'versions_seen', 'faces_seen']
        return summary.reset_index()
