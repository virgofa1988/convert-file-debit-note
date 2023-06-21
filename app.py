from flask import Flask, request, send_file
import pandas as pd
import os
import datetime

BASE_DIR = os.getcwd()
FILE_PATH = os.path.join(BASE_DIR, 'sorted_file.txt')

format_spec = [10, 2, 8, 4, 8, 30, 12, 12, 8, 4, 6, 4, 4, 4, 12, 6, 8]
# Fixed fields
fixed_fields = {
    0: 'EX00000000',  # First 10 characters
    1: 'MD',  # TRANSACTION TYPE
    11: '050',  # LEVEL_ONE_CODE
    12: '1',  # LEVEL_TWO_CODE
    13: '',  # LEVEL_THREE_CODE
    16: '',  # CHECKSUM
}
# Mapping from positions in the fixed-length text file to CSV field names
field_mapping = {
    2: 'Service_Group',  # TRANS_ID - DX Number
    3: 'Branch_Code',  # 'BRANCH_CODE',
    4: 'Surcharges_Date',  # 'TRANS_DATE', Format YYYYMMDD
    5: 'Statement_Details',  # 'TRANS_DESCR'
    6: 'Base_Amount',  # 'TRANS_AMOUNT'--> NET_Amount
    7: 'GST_amount',  # 'TRANS_GST',
    8: 'Customer_ID',  # 'CUSTOMER_NO',
    9: 'Service_Code',  # 'SERVICE_CODE',
    10: 'GL_Account',  # 'ACCOUNT_CODE',
    14: 'Base_Amount',  # POSTED_AMOUNT' -- NET Amount
    15: 'No_item',  # 'NBR_ITEMS', 999999
}


def format_fixed_length(fields, format_spec):
    result = []
    # Output of zip: [('a', 1), ('b', 2), ('c', 3)]
    for i, (field, width) in enumerate(zip(fields, format_spec)):
        # print('field, width, i', field, width, i)
        if i in {6, 7, 14, 15}:  # for TRANS_AMOUNT, TRANS_GST, POSTED_AMOUNT, and NBR_ITEMS
            result.append(str(field).zfill(width))  # add leading zeros
        else:
            # truncate and/or add trailing spaces
            result.append(str(field)[:width].ljust(width))
    return ''.join(result)


def convert_csv_to_fixed_length(input_csv, output_txt, format_spec, fixed_fields, field_mapping):
    df = pd.read_csv(input_csv)

    with open(output_txt, 'w') as f:
        for _, row in df.iterrows():
            # Initialize fields with fixed values by using List Comprehensions method
            # Len(format_spec) provide 16 fields for txt file
            # ['EX00000000', 'MD', '', '', '', '', '', '', '', '', '', '050', '1', '', '', '', '']
            fields = [fixed_fields.get(i, '') for i in range(len(format_spec))]

            # print('row', row)
            # print('fields', fields)

            # Overwrite above fields with values from CSV file according to field_mapping
            for key, csv_field in field_mapping.items():
                fields[key] = row[csv_field]
                # print('csv_field', csv_field)
                # print('Field[i]', fields[i], i)
            f.write(format_fixed_length(fields, format_spec) + '\n')


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             return 'No file part'
#         file = request.files['file']
#         if file.filename == '':
#             return 'No selected file'
#         if file:
#             try:
#                 convert_csv_to_fixed_length(
#                     file, FILE_PATH, format_spec, fixed_fields, field_mapping)
#             except Exception as e:
#                 return f'Error processing file: {e}'
#             return f'''
#             <!doctype html>
#             <title>File Converted</title>
#             <h1>File converted successfully!</h1>
#             <a href="/download">Click here to download the converted file</a>
#             '''
#     return '''
#     <!doctype html>
#     <title>Upload a CSV File</title>
#     <h1>Upload a CSV file to convert</h1>
#     <form method=post enctype=multipart/form-data>
#       <input type=file name=file>
#       <input type=submit value=Upload>
#     </form>
#     '''
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            try:
                convert_csv_to_fixed_length(
                    file, FILE_PATH, format_spec, fixed_fields, field_mapping)
            except Exception as e:
                return f'Error processing file: {e}'
            return f'''
            <!doctype html>
            <title>File Converted</title>
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <h1 class="text-center">File converted successfully!</h1>
                        <div class="text-center">
                            <a href="/download" class="btn btn-success">Click here to download the converted file</a>
                        </div>
                    </div>
                </div>
            </div>
            '''
    return '''
    <!doctype html>
    <title>Upload a CSV File</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <h1 class="text-center">Upload a CSV file to convert</h1>
                <form method=post enctype=multipart/form-data>
                  <div class="form-group">
                    <input type=file name=file class="form-control">
                  </div>
                  <div class="form-group">
                    <input type=submit value=Upload class="btn btn-primary">
                  </div>
                </form>
            </div>
        </div>
    </div>
    '''


@app.route('/download')
def download_file():
    if os.path.exists(FILE_PATH):
        return send_file(FILE_PATH, as_attachment=True)
    else:
        return 'No file to download'


if __name__ == '__main__':
    # Default to port 5005 if PORT isn't set
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port)
