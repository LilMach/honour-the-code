import tkinter as tk
from tkinter import filedialog
import boto3
import json
import fitz
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import os
import time

uploaded_file_path = None
result_label = None

# Upload button and file selection logic - come back...
def browse_file():
    global uploaded_file_path
    file_path = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png"), ("PDF Files", "*.pdf")])
    if file_path:
        s3 = boto3.client("s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        bucket_name = "bucket-image-processing"  # Replace with your S3 bucket name
        file_name = os.path.basename(file_path)  # Use the original file name
        s3.upload_file(file_path, bucket_name, file_name)
        uploaded_file_path = file_name
        upload_status_label.config(text=f"File '{file_name}' has been successfully uploaded.")
# Function to wait for Lambda function completion and fetch its output
def generate_filled_form(input_data):
    # Invoke Textract Lambda function
    # Create a boto3 Lambda client
    lambda_client = boto3.client("lambda",
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key,
                                 region_name=aws_region)

    # Define the name of your Lambda function
    function_name = 'imageprocessing'

    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',  # Use 'RequestResponse' for synchronous invocation
        Payload=json.dumps(input_data)
    )

    # Parse and use the response from the Lambda function
    response_payload = response['Payload'].read().decode('utf-8')

    # Assuming your Lambda function returns JSON data, parse it
    parsed_response = json.loads(response_payload)

    return parsed_response

def find_most_similar_key(target_key, keys_to_compare):
    return process.extractOne(target_key, keys_to_compare, scorer=fuzz.ratio)

def update_dict(dict1, dict2, threshold=20):
    updated_dict2 = dict2.copy()

    for key1 in dict1.keys():
        most_similar_key, score = find_most_similar_key(key1, dict2.keys())

        no_spaces = ''.join(key1.split())

        for i in range(2, 5):
            if no_spaces == "GivenName(" + str(i) + "):":
                most_similar_key = "cc.name giv " + str(i)

        if score >= threshold:
            updated_dict2[most_similar_key] = dict1[key1]

    return updated_dict2

def update_doc(doc, dict2):

    for page in doc:
        for w in page.widgets():
            if w.field_name in dict2:
                w.field_value = dict2[w.field_name]
                w.update()
    output_pdf_path = 'doc.pdf'
    doc.save(output_pdf_path)

def download_pdf():
    global result_label  # Make result_label a global variable

    # Specify the file save dialog options
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])

    # Check if the user canceled the file save dialog
    if not file_path:
        return

    try:
        # Check if the "doc.pdf" file exists in the current directory
        if os.path.exists("doc.pdf"):
            # Rename and move the "doc.pdf" file to the user-specified location
            os.rename("doc.pdf", file_path)
            result_label.config(text="PDF downloaded successfully.")
        else:
            result_label.config(text="No PDF file to download.")
    except Exception as e:
        result_label.config(text=f"Error: {str(e)}")

def strip_dict(scanned_doc):
    output_dict = {}

    for key, value in scanned_doc.items():
        # Remove square brackets and whitespace from the value
        stripped_value = value[0].strip('[] ')
        output_dict[key] = stripped_value
    return output_dict

if __name__ == "__main__":

    #Setting Up AWS Connection
    aws_access_key_id = "AKIAYIJXM3NSD62GRVMD"
    aws_secret_access_key = "r8H6iaILCNimaTY4LYOQ/xCEHiB3rgnPyVbquC7O"
    aws_region = "ap-southeast-2"  # Replace with your AWS region, e.g., "us-east-1"

    log_group_name = '/aws/lambda/imageprocessing'
    lambda_response = None

    # File Information
    filename = "NewClientIntakeForm.png"
    doc_path = "956-Template.pdf"
    doc = fitz.open(doc_path)

    #Update dictionary with new information
    input_data = {
        "Records": [
            {
                "eventVersion": "2.0",
                "eventSource": "aws:s3",
                "awsRegion": "us-east-1",
                "eventTime": "1970-01-01T00:00:00.000Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                    "principalId": "EXAMPLE"
                },
                "requestParameters": {
                    "sourceIPAddress": "127.0.0.1"
                },
                "responseElements": {
                    "x-amz-request-id": "EXAMPLE123456789",
                    "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "testConfigRule",
                    "bucket": {
                        "name": "bucket-image-processing",
                        "ownerIdentity": {
                            "principalId": "EXAMPLE"
                        },
                        "arn": "arn:aws:s3:::example-bucket"
                    },
                    "object": {
                        "key": filename,
                        "size": 1024,
                        "eTag": "0123456789abcdef0123456789abcdef",
                        "sequencer": "0A1B2C3D4E5F678901"
                    }
                }
            }
        ]}
    dict_scanned_doc = generate_filled_form(input_data)

    dict_pdf_template = {'cc.name fam': 'blank',
                         'cc.name giv': 'blank',
                         'cc.dob': 'blank',
                         'cc.resadd str': 'blank',
                         'cc.resadd pc': 'blank',
                         'cc.diac id' : 'blank',
                         'cc.mob': 'blank',
                         'cc.name fam 2': 'blank',
                         'cc.name giv 2': 'blank',
                         'cc.name fam 3': 'blank',
                         'cc.name giv 3': 'blank',
                         'cc.name fam 4': 'blank',
                         'cc.name giv 4': 'blank',
                         'ta.type': 'blank',
                         'ta.lodged': 'blank',
                         'ta.specific matter': 'blank',
                         'ta.diac request id': 'blank',
                         'ta.diac trans id': 'blank',
                         }

    updated_dict = update_dict(strip_dict(dict_scanned_doc), dict_pdf_template)

    # MAKING PROGRAM
    root = tk.Tk()
    root.title("Automated Immigration Form Filler")

    # Create and configure GUI elements
    document_label = tk.Label(root, text="What is the document you want to fill?")
    document_label.pack()

    # Dropdown for document selection
    document_var = tk.StringVar(root)
    document_var.set("Migration Law Form 956")
    document_dropdown = tk.OptionMenu(root, document_var, "Migration Law Form 956")
    document_dropdown.pack()

    professional_label = tk.Label(root, text="Select the legal professional:")
    professional_label.pack()

    # Dropdown for legal professional selection
    professional_var = tk.StringVar(root)
    professional_var.set("Harvey Specter")
    professional_dropdown = tk.OptionMenu(root, professional_var, "Harvey Specter")

    professional_dropdown.pack()

    upload_button = tk.Button(root, text="Upload documents", command=browse_file)
    upload_button.pack()

    upload_status_label = tk.Label(root, text="")
    upload_status_label.pack()

        # Button to generate the filled PDF form
    generate_button = tk.Button(root, text="Generate Filled PDF", command=update_doc(doc, updated_dict))

    # Button to download the filled PDF form
    download_button = tk.Button(root, text="Download the Filled PDF", command=download_pdf)
    download_button.pack()

    # Create the result_label and configure it
    result_label = tk.Label(root, text="")
    result_label.pack()
        # Start the Tkinter main loop
    root.mainloop()
