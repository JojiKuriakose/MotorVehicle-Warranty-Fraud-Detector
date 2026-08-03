import io
from config.settings import settings
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from pypdf import PdfReader

# 1. Define storage details
account_url = settings.storage_account_url
container_name = settings.container_name
blob_name = settings.blob_name

# 2. Setup secure Azure authentication
credential = DefaultAzureCredential()

# 3. Initialize Blob Service Client
blob_service_client = BlobServiceClient(account_url, credential=credential)
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

# 4. Stream blob bytes into memory
downloader = blob_client.download_blob()
blob_bytes = downloader.readall()

# 5. Load bytes into an in-memory stream using BytesIO
pdf_stream = io.BytesIO(blob_bytes)

# 6. Parse the PDF (Example using pypdf)
pdf_reader = PdfReader(pdf_stream)

#7. Extract text from the first page as a test
policy_text = pdf_reader.pages
