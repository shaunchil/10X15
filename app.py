from flask import Flask, render_template, request, send_file
from azure.storage.blob import BlobServiceClient, BlobClient
import os
from io import BytesIO

app = Flask(__name__)

# Define your constants here
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=10x15;AccountKey=cRZUjzLbkheGk1YZ1OoHtfSrIbJzlLRBd3OV5zTWTinC1F57Zc0CKBR2yxSjv82Qd6bMZ5nGkJUU+AStF3j/PA==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "audio-files"
SAS_TOKEN = "sp=r&st=2024-08-21T00:35:42Z&se=2025-08-21T08:35:42Z&sv=2022-11-02&sr=c&sig=Ml2H%2FGr2bPixWFh%2FAXspUHYKf%2FwiH9LL8CHSrdURABw%3D"

@app.route('/')
def index():
    # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    # List blobs in the container
    blob_list = container_client.list_blobs()

    # Organize blobs by folders
    folder_dict = {}
    for blob in blob_list:
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
        container_name=CONTAINER_NAME
    )

@app.route('/download_files', methods=['POST'])
def download_files():
    print("Download files route hit")  # Log to check if the route is accessed

    selected_files = request.form.getlist('file')

    if not selected_files:
        return "No files selected.", 400

    # For simplicity, handle only one file at a time for now
    file_url = selected_files[0]

    # Extract the file name from the URL
    file_name = file_url.split('/')[-1].split('?')[0]

    # Create a BlobClient to download the file
    blob_client = BlobClient.from_blob_url(file_url)

    # Download the file into a stream
    stream = BytesIO()
    blob_client.download_blob().readinto(stream)
    stream.seek(0)

    # Send the file to the client as a download
    return send_file(
        stream,
        as_attachment=True,
        download_name=file_name
    )

if __name__ == '__main__':
    app.run(debug=True)
