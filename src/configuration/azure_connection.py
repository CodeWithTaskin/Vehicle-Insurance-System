from azure.storage.blob import BlobServiceClient
import os

class AzureBlobClient:
    blob_service_client = None

    def __init__(self):
        if AzureBlobClient.blob_service_client is None:
            conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            if not conn_str:
                raise Exception("AZURE_STORAGE_CONNECTION_STRING not set in environment.")
            AzureBlobClient.blob_service_client = BlobServiceClient.from_connection_string(conn_str)

        self.blob_service_client = AzureBlobClient.blob_service_client