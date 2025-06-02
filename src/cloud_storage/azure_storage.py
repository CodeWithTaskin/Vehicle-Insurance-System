import os
import pickle
from src.configuration.azure_connection import AzureBlobClient
from azure.storage.blob import ContentSettings
from io import BytesIO, StringIO
import pandas as pd

class AzureStorageService:
    def __init__(self):
        self.client = AzureBlobClient().blob_service_client

    def upload_file(self, local_path, container_name, blob_path, remove=True):
        blob_client = self.client.get_blob_client(container=container_name, blob=blob_path)
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        if remove:
            os.remove(local_path)

    def upload_df_as_csv(self, df, local_path, blob_path, container_name):
        df.to_csv(local_path, index=False)
        self.upload_file(local_path, container_name, blob_path)

    def create_folder(self, container_name, folder_path):
        if not folder_path.endswith("/"):
            folder_path += "/"
        blob_client = self.client.get_blob_client(container=container_name, blob=folder_path)
        blob_client.upload_blob("", overwrite=True)

    def blob_exists(self, container_name, blob_path):
        blob_client = self.client.get_blob_client(container=container_name, blob=blob_path)
        return blob_client.exists()

    def get_blob_as_dataframe(self, container_name, blob_path):
        blob_client = self.client.get_blob_client(container=container_name, blob=blob_path)
        stream = blob_client.download_blob()
        return pd.read_csv(BytesIO(stream.readall()))

    def get_blob_as_object(self, container_name, blob_path):
        blob_client = self.client.get_blob_client(container=container_name, blob=blob_path)
        stream = blob_client.download_blob()
        return pickle.loads(stream.readall())

    def upload_object(self, obj, container_name, blob_path):
        blob_client = self.client.get_blob_client(container=container_name, blob=blob_path)
        blob_client.upload_blob(pickle.dumps(obj), overwrite=True)

    def list_blobs(self, container_name, prefix=""):
        return self.client.get_container_client(container_name).list_blobs(name_starts_with=prefix)