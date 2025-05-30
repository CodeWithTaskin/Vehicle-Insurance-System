import sys
import pandas as pd
import numpy as np
from typing import Optional


from src.configuration.mongo_db_connection import MongoDBClient
from src.constants import *
from src.exception import MyException


class Proj1Data:
    '''
    A class to export MongoDB records as a pandas DataFrame.
    '''
    def __init__(self) -> None:
        '''
        Initializes the MongoDB client connection.
        '''
        try:
            self.mongo_client = MongoDBClient(database_name=DATABASE_NAME)
        except Exception as e:
            raise MyException(e, sys)
    
    def export_collection_as_dataframe(self, collection_name : str, database_name : Optional[str] = None) -> pd.DataFrame:
        '''
        Exports an entire MongoDB collection as a pandas DataFrame.
        '''
        try:
            # Access Specified collection from the default or specified database
            if database_name is None:
                collection = self.mongo_client.database[collection_name]
            else:
                collection = self.mongo_client[database_name][collection_name]
                
            
            print('Fetching data from mongoDB')
            df = pd.DataFrame(list(collection.find()))
            print(f'Data fetched with len: {len(df)}')

            
            if '_id' in df.columns.to_list():
                df = df.drop(columns=['_id'], axis=1)
                
            if 'id' in df.columns.to_list():
                df = df.drop(columns=['id'], axis=1)
                
            df.replace({'na':np.nan}, inplace = True)
            
            return df
        
        except Exception as e:
            raise MyException(e, sys)
        
