import sys
import numpy as np
import pandas as pd

from imblearn.combine import SMOTEENN
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.compose import ColumnTransformer

from src.constants import *
from src.entity.config_entity import DataTransformationConfig
from src.entity.artifact_entity import DataTransformationArtifact, DataIngestionArtifact, DataValidationArtifact
from src.exception import MyException
from src.logger import logging
from src.utils.main_utils import *


class DataTransformation:
    def __init__(self, data_ingestion_artifact : DataIngestionArtifact,
                 data_transformation_config : DataTransformationArtifact,
                 data_validation_artifact : DataValidationArtifact):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_transformation_config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact
            self._schema_config = read_yaml(file_path=SCHEMA_FILE_PATH)
        
        except Exception as e:
            raise MyException(e, sys) from e
    @staticmethod   
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        
        except Exception as e:
            raise MyException(e, sys) from e
        
    
    def get_data_transformer_object(self) -> Pipeline:
        '''
        Creates and returns a data transformer object for the data,
        including gender mapping, dummy variable creation, column renaming,
        feature sealing, and type adjustments.
        '''
        logging.info('Entered get_data_transformer_object method of DataTransformation class')
        
        try:
            # Initialize transformers
            numeric_transformer = StandardScaler()
            min_max_scaler = MinMaxScaler()
            logging.info('Transformers Initialized : StandardScaler-MinMaxSca')
            
            # Load schema configuration
            num_features = self._schema_config['num_features']
            mm_columns = self._schema_config['mm_columns']
            logging.info('Cols loaded from schema')
            
            # Creating preprocessor pipeline
            preprocessor = ColumnTransformer(
                transformers=[
                    ('StandardScaler', numeric_transformer, num_features),
                    ('MinMaxScaler', min_max_scaler, mm_columns)
                ],
                remainder='passthrough' #Leaves other columns as they are
            )
            
            #Wrapping everything in a single pipeline
            final_pipeline = Pipeline(steps=[('Preprocessor', preprocessor)])
            logging.info('Final Pipeline Ready!!')
            logging.info('Exited get_data_transformer_object method of DataTransformation class')
            
            return final_pipeline
        
        except Exception as e:
            raise MyException(e, sys) from e
        
    
    def _map_gender_column(self, df : pd.DataFrame) -> pd.DataFrame:
        ''' Map Gender column to 0 for Female and 1 for Male.'''
        try:
            
            logging.info('Mapping "Gender" column to binary values')
            df['Gender'] = df['Gender'].map({'Female':0, 'Male':1}).astype(int)
            return df
        
        except Exception as e:
            raise MyException(e, sys) from e
    
    def _create_dummy_columns(self, df : pd.DataFrame) -> pd.DataFrame:
        ''' Create dummy variables for categorical features. '''
        try:
            
            logging.info('Creating dummy variables for categorical features')
            df = pd.get_dummies(df, drop_first=True)
            return df
        
        except Exception as e:
            raise MyException(e, sys) from e
    
    def _rename_columns(self, df : pd.DataFrame) -> pd.DataFrame:
        ''' Rename specific columns and ensure integer types for dummy columns. '''
        try:

            logging.info('Renaming spcific columns and casting to int')
            df = df.rename(columns = {
                'Vehicle_Age_< 1 Year': 'Vehicle_Age_It_1_Year',
                'Vehicle_Age_> 2 Year': 'Vehicle_Age_gt_2_Years'
            })
            for col in ['Vehicle_Age_It_1_Year','Vehicle_Age_gt_2_Years','Vehicle_Damage_Yes']:
                if col in df.columns:
                    df[col] = df[col].astype('int')
            return df
        
        except Exception as e:
            raise MyException(e, sys) from e
    
    def _drop_id_column(self, df : pd.DataFrame) -> pd.DataFrame:
        ''' Drop the "id" column if it exists. '''
        try:
            
            logging.info('Dropping "id" column')
            drop_col = self._schema_config['drop_columns']
            if drop_col in df.columns:
                df = df.drop(drop_col, axis=1)
            return df
        
        except Exception as e:
            raise MyException(e, sys) from e
    
    
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        '''
        Initiates the data transformation component for the pipeline.
        '''
        try:
            
            logging.info('Data Transformation Started !!!')
            # if not self.data_validation_artifact.validation_status:
            #     raise Exception(self.data_validation_artifact.message)
            
            # Load train and test data
            train_df = self.read_data(file_path=self.data_ingestion_artifact.trained_file_path)
            test_df = self.read_data(file_path=self.data_ingestion_artifact.test_file_path)
            logging.info('Train-Test data loaded.')
            
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            logging.info('Input and Target cols defined for doth train and test df.')
            
            # Apply custom transformations in specified sequence
            logging.info('Custom transformation Started')
            input_feature_train_df = self._map_gender_column(input_feature_train_df)
            input_feature_train_df = self._drop_id_column(input_feature_train_df)
            input_feature_train_df = self._create_dummy_columns(input_feature_train_df)
            input_feature_train_df = self._rename_columns(input_feature_train_df)
            
            input_feature_test_df = self._map_gender_column(input_feature_test_df)
            input_feature_test_df = self._drop_id_column(input_feature_test_df)
            input_feature_test_df = self._create_dummy_columns(input_feature_test_df)
            input_feature_test_df = self._rename_columns(input_feature_test_df)
            logging.info('Custom transformation applied Successfully 😊😊')
            
            logging.info('Starting data transformation')
            preprocessior = self.get_data_transformer_object()
            logging.info('Got the preprecessor object')
            
            logging.info('Initializing transformation for Training data')
            input_feature_train_arr = preprocessior.fit_transform(input_feature_train_df)
            logging.info('Initializing transformation for Testing data')
            input_feature_test_arr = preprocessior.transform(input_feature_test_df)
            logging.info('transformation done end to end to train-test df.')
            
            logging.info('Applying SMOTEENN for handling imbalanced dataset.')
            smt = SMOTEENN(sampling_strategy='minority')
            input_feature_train_final, target_feature_train_df = smt.fit_resample(
                input_feature_train_arr, target_feature_train_df
            )
            input_feature_test_final, target_feature_test_final = smt.fit_resample(
                input_feature_test_arr, target_feature_test_df
            )
            logging.info('SMOTEENN applied to train-test df.')
            
            train_arr = np.c_[input_feature_train_final, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_final, np.array(target_feature_test_final)]
            logging.info('feature target concatenation done for train-test df.')
            
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessior)
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array = train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array = test_arr)
            logging.info('Saving transformation object and transformed files.')
            
            logging.info('Data transformation completed successfully')
            return DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            
        except Exception as e:
            raise MyException(e, sys) from e