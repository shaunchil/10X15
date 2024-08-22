from azure.storage.blob import BlobServiceClient

# Use the correct connection string here
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=10x15;AccountKey=cRZUjzLbkheGk1YZ1OoHtfSrIbJzlLRBd3OV5zTWTinC1F57Zc0CKBR2yxSjv82Qd6bMZ5nGkJUU+AStF3j/PA==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "audio-files"
SAS_TOKEN = "sp=r&st=2024-08-21T00:35:42Z&se=2025-08-21T08:35:42Z&sv=2022-11-02&sr=c&sig=Ml2H%2FGr2bPixWFh%2FAXspUHYKf%2FwiH9LL8CHSrdURABw%3D"  # SAS token generated from Azure portal or programmatically

def generate_html(blob_list, sas_token):
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Audio Files Directory</title>
        <style>
            body {font-family: Arial, sans-serif;}
            h2 {margin-top: 20px;}
            ul {list-style-type: none; margin-left: 20px;}
            li {margin-bottom: 5px;}
            .fixed-button {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            .container {
                padding-bottom: 60px; /* To ensure content is not hidden behind the button */
            }
        </style>
    </head>
    <body>
        <h1>JESUS Film (Story of JESUS) Audio Radio Temporary Files Directory</h1>
        <form id="downloadForm" method="post" action="http://localhost:5000/download_files" target="_blank">
            <div class="container">
    '''

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

    # Generate HTML content based on the folder structure
    for folder, files in folder_dict.items():
        if folder:  # Only add folder name if it's not the root
            html_content += f'<h2>{folder}</h2>\n<ul>\n'
        else:
            html_content += '<ul>\n'

        for file_name in files:
            file_url = f"https://{CONNECTION_STRING.split(';')[1].split('=')[1]}.blob.core.windows.net/{CONTAINER_NAME}/{folder}/{file_name}?{sas_token}"
            html_content += f'<li><input type="checkbox" name="file" value="{file_url}"> <a href="{file_url}" target="_blank">{file_name}</a></li>\n'

        html_content += '</ul>\n'

    html_content += '''
            </div>
            <button type="submit" class="fixed-button">Download Selected Files</button>
        </form>
    </body>
    </html>
    '''

    return html_content

def main():
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    blob_list = container_client.list_blobs()
    html_content = generate_html(blob_list, SAS_TOKEN)

    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

    print('HTML file generated: index.html')

if __name__ == '__main__':
    main()
