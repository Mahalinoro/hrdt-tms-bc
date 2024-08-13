import pandas as pd
import glob
import json
import re
from progressbar import progressbar

# Generator to read JSON lines from files
def json_line_generator(file_list):
    pattern = ['A(\d+)', '(\d+){1}']
    for file_path in file_list:
        a = re.search(r'A(\d+)', file_path).group(1)
        b = re.search(pattern[1], file_path).group()
        with open(file_path, 'r') as file:
            for line in file:
                yield json.loads(line), a, int(b)

file_list = glob.glob("./raw_datasets/ModifiedVeremi/RandomSpeed/*.json")
chunk_size = 10000  # Adjust the chunk size as needed
features = []
labels = {}

output_csv_path = './raw_datasets/RandomSpeed.csv'

# Initialize CSV file with headers
pd.DataFrame(columns=[
    'receiver', 'sender', 'sendTime', 'messageID', 'pos_x1', 'pos_y1', 'spd_x1', 'spd_y1', 'spd_z1', 
    'acl1', 'hed_x1', 'hed_y1'
]).to_csv(output_csv_path, index=False)

print("Processing files:")
for json_object, a, b in progressbar(json_line_generator(file_list)):
    if json_object['type'] == 2:
        continue
    else:
        labels[b] = a
        features.append({
            'receiver': b,
            'sender': json_object['sender'],
            'sendTime': json_object['sendTime'],
            'messageID': json_object['messageID'],
            'pos_x1': json_object['pos'][0],
            'pos_y1': json_object['pos'][1],
            'spd_x1': json_object['spd'][0],
            'spd_y1': json_object['spd'][1],
            'spd_z1': json_object['spd'][0],
            'acl1': json_object['acl'][1],
            'hed_x1': json_object['hed'][0],
            'hed_y1': json_object['hed'][1],
        })

    # Write chunk to CSV and clear the features list
    if len(features) >= chunk_size:
        pd.DataFrame(features).to_csv(output_csv_path, mode='a', header=False, index=False)
        features = []

# Write any remaining data to CSV
if features:
    pd.DataFrame(features).to_csv(output_csv_path, mode='a', header=False, index=False)

print("Converting into CSV [DONE]")

print('Relabeling data...')
data = pd.read_csv(output_csv_path)
data['AttackerType'] = data['sender'].map(labels)
data.to_csv(output_csv_path, index=False)
print('Relabeling data [DONE]')