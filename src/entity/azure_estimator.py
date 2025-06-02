import sys
from src.cloud_storage.azure_storage import AzureStorageService
from src.exception import MyException
from src.entity.estimator import MyModel
from pandas import DataFrame

class Proj1Estimator:
    def __init__(self, container_name: str, model_path: str):
        self.container_name = container_name
        self.model_path = model_path
        self.azure = AzureStorageService()
        self.loaded_model: MyModel = None

    def is_model_present(self, model_path: str) -> bool:
        try:
            return self.azure.blob_exists(container_name=self.container_name, blob_path=model_path)
        except MyException as e:
            print(e)
            return False

    def load_model(self) -> MyModel:
        try:
            return self.azure.get_blob_as_object(container_name=self.container_name, blob_path=self.model_path)
        except Exception as e:
            raise MyException(e, sys)

    def save_model(self, from_file: str, remove: bool = False) -> None:
        try:
            self.azure.upload_file(local_path=from_file,
                                   blob_path=self.model_path,
                                   container_name=self.container_name,
                                   remove=remove)
        except Exception as e:
            raise MyException(e, sys)

    def predict(self, dataframe: DataFrame):
        try:
            if self.loaded_model is None:
                self.loaded_model = self.load_model()
            return self.loaded_model.predict(dataframe=dataframe)
        except Exception as e:
            raise MyException(e, sys)