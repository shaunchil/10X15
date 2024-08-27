from flask import Flask, render_template, request, send_file
from azure.storage.blob import BlobServiceClient, BlobClient
import os
from io import BytesIO
import zipfile
import math  # Import to handle pagination calculations

app = Flask(__name__)

# Define your constants here
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=10x15;AccountKey=cRZUjzLbkheGk1YZ1OoHtfSrIbJzlLRBd3OV5zTWTinC1F57Zc0CKBR2yxSjv82Qd6bMZ5nGkJUU+AStF3j/PA==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "audio-files"
SAS_TOKEN = "sp=r&st=2024-08-21T00:35:42Z&se=2025-08-21T08:35:42Z&sv=2022-11-02&sr=c&sig=Ml2H%2FGr2bPixWFh%2FAXspUHYKf%2FwiH9LL8CHSrdURABw%3D"
FILES_PER_PAGE = 400  # Number of files per page for pagination

@app.route('/')
def index():
    # Get the current page number from the query string; default is 1
    page = int(request.args.get('page', 1))

    # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    # List blobs in the container
    blob_list = list(container_client.list_blobs())  # Convert to list to allow slicing

    # Calculate pagination details
    total_files = len(blob_list)
    total_pages = math.ceil(total_files / FILES_PER_PAGE)
    start_index = (page - 1) * FILES_PER_PAGE
    end_index = start_index + FILES_PER_PAGE
    paginated_blobs = blob_list[start_index:end_index]

    # Organize blobs by folders for the current page
    folder_dict = {}
    for blob in paginated_blobs:
        parts = blob.name.split('/')
        if len(parts) > 1:
            folder_name = parts[0]
            file_name = '/'.join(parts[1:])
            if folder_name not in folder_dict:
                folder_dict[folder_name] = []
            folder_dict[folder_name].append(file_name)
        else:
            if '' not in folder_dict:
                folder_dict[''] = []
            folder_dict[''].append(parts[0])

    # Pass the necessary variables to the template
    return render_template(
        'index.html',
        folder_dict=folder_dict,
        sas_token=SAS_TOKEN,
        connection_string=CONNECTION_STRING,
        container_name=CONTAINER_NAME,
        page=page,
        total_pages=total_pages
    )

@app.route('/download_files', methods=['POST'])
def download_files():
    selected_files = request.form.getlist('file')

    if not selected_files:
        return "No files selected.", 400

    if len(selected_files) == 1:
        # For a single file, download it directly
        file_url = selected_files[0]
        file_name = file_url.split('/')[-1].split('?')[0]
        blob_client = BlobClient.from_blob_url(file_url)
        stream = BytesIO()
        blob_client.download_blob().readinto(stream)
        stream.seek(0)
        return send_file(
            stream,
            as_attachment=True,
            download_name=file_name
        )
    else:
        # For multiple files, create a zip archive
        zip_stream = BytesIO()
        with zipfile.ZipFile(zip_stream, 'w') as zipf:
            for file_url in selected_files:
                file_name = file_url.split('/')[-1].split('?')[0]
                blob_client = BlobClient.from_blob_url(file_url)
                file_stream = BytesIO()
                blob_client.download_blob().readinto(file_stream)
                file_stream.seek(0)
                zipf.writestr(file_name, file_stream.read())
        zip_stream.seek(0)
        return send_file(
            zip_stream,
            as_attachment=True,
            download_name="selected_files.zip"
        )

if __name__ == '__main__':
    app.run(debug=True)
