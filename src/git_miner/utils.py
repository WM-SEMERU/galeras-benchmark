import json
import random
import os



"""
Removes Duplicates from a json file given a key
file: name of file
_key: key used to remove duplicated by

produces two jsons, one containing unique elements and one containing duplicates
"""


def removeDuplicates(file, _key):
    with open(file, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        unique_elements = []
        cleaned_data = []
        duplicated_data = []
        keys = []
        for i, j in enumerate(data):
            if data[i][_key] not in unique_elements:
                unique_elements.append(data[i][_key])
                keys.append(i)
            else:
                duplicated_data.append(data[i][_key])
        for key in keys:
            cleaned_data.append(data[key])

        print(
            "Total duplicates removed: {}, Total items: {}, Final items:{}".format(
                (len(data) - len(unique_elements)),
                len(data), len(unique_elements)))
        print("Final items in list: {}".format(len(cleaned_data)))

        with open(f'complete/path/to/where/you/want/to.save/your/file/with/filename', 'a',
                  encoding='utf8') as wr:
            json.dump(cleaned_data, wr, indent=4)
        with open(f'complete/path/to/where/you/want/to.save/your/file/with/filename', 'a',
                  encoding='utf8') as dr:
            json.dump(duplicated_data, dr, indent=4)


"""
Filter json file based on certain property
path: path to the directory
"""


def filterData(path):
    with open(path, 'r+', encoding='utf8') as f:
        print("reading file:", path, "/")
        data = json.load(f)
        # number of filters can be changed here, you can add a logical operator and add more filters as per your need
        filtered_data = [x for x in data if 20 < x['token_counts'] < 2024]

        with open(f'complete/path/to/where/you/want/to.save/your/file/with/filename', 'a',
                  encoding='utf8') as wr:
            json.dump(filtered_data, wr, indent=4)


"""
Combine json present a directory
path: path to the directory
"""


def combineAllJson(path):
    finalJSON = list()
    json_file_names = [filename for filename in os.listdir(path) if filename.endswith('.json')]

    for json_file_name in json_file_names:
        with open((os.path.join(path, json_file_name)), 'r') as infile:
            finalJSON.extend(json.load(infile))

    with open(f'complete/path/to/where/you/want/to.save/your/file/with/filename', 'a') as output_file:
        json.dump(finalJSON, output_file)


"""
Can be used for both random split and 
path:str : path to the file to be processed
"""


def codeCompletionSplit(path):
    with open(path, 'r') as file:
        data1 = json.load(file)

    modified_data = []

    for entry in data1:
        random_number = round(random.uniform(0.4, 0.65), 10)
        code = str(entry['code'])  # Convert code value to string
        signature = code.split(":", 1)
        mid_index = (int)(len(code) * random_number)

        # Find the index of the last space before the middle index
        split_index = code.rfind(' ', 0, mid_index)

        if split_index != -1:
            # Split the code at the space index
            modified_code = code[:split_index].strip()
        else:
            # If no space is found, split at the middle index
            modified_code = code[:mid_index].strip()

        # this can be modified in any format you want your destination file to be in
        modified_entry = {
            'repo': entry['repo'],
            'path': entry['path'],
            'file_name': entry['file_name'],
            'fun_name': entry['fun_name'],
            'commit_message': entry['commit_message'],
            'code': entry['code'],
            'random_split': str(modified_code),
            'signature': signature[0],
            'tested_class': "",
            'docstring': entry['doctring'],
            'url': entry['url'],
            'language': entry['language'],
            'ast_errors': entry['ast_errors'],
            'n_ast_errors': entry['n_ast_errors'],
            'ast_levels': entry['ast_levels'],
            'n_whitespaces_': entry['n_whitespaces_'],
            'complexity': entry['complexity'],
            'nloc': entry['nloc'],
            'token_counts': entry['token_counts'],
            'n_ast_nodes': entry['n_ast_nodes']
        }
        modified_data.append(modified_entry)

    with open('complete/path/to/where/you/want/to.save/your/file/with/filename', 'w') as file:
        json.dump(modified_data, file, indent=4)
# combineAllJson()
# removeDuplicates('/Users/dipinkhati/custom_dataset_openai/tiktoken/codeSummarizationCustom.json', "fun_name")
# get all JSON file names as a list

# filterData('/Users/dipinkhati/custom_dataset_openai/tiktoken/manuallyCleanedDocstring.json',0)
