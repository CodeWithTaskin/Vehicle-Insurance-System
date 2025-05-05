import os
from datetime import datetime


# For MongoDB connection
DATABASE_NAME = 'Proj1'
COLLECTION_NAME = 'Proj1_Data'
MONGODB_URL_KEY = 'MONGODB_URL'

PIPELINE_NAME: str = ''
ARTIFACT_DIR: str = 'artifact'

MODEL_FILE_NAME = 'model.pkl'

TARGET_COLUMN = 'Response'
CURRENT_YEAR = datetime.today().year
PREPROCESSING_OBJECT_FILE_NAME = 'preprocessing.pkl'

FILE_NAME: str = 'data.csv'
TRAIN_FILE_NAME: str = 'train.csv'
TEST_FILE_NAME: str = 'test.csv'
SCHEMA_FILE_PATH = os.path.join('config', 'schema.yaml')


AZURE_ACCESS_KEY_ID_ENV_KEY = 'AZURE_ACCESS_KEY_ID'
AZURE_SECRET_ACCESS_KEY_ENV_KEY = 'AZURE_SECRET_ACCESS_KEY'
REGION_NAME = ''

'''
Data Ingestion related constant starts with DATA_INGESTION var name.
'''

DATA_INGESTION_COLLECTION_NAME: str = 'Proj1_Data'
DATA_INGESTION_DIR_NAME: str = 'data_ingestion'
DATA_INGESTION_FEATURE_STORE_DIR: str = 'feature_store'
DATA_INGESTION_INGESTED_DIR: str = 'ingested'
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.25

