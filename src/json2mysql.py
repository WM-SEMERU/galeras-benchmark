import pymysql, os, json, glob

# do validation and checks before insert
def validate_string(val):
   if val != None:
        if type(val) is int:
            #for x in val:
            #   print(x)
            return str(val).encode('utf-8')
        else:
            val = str(val).replace("'","\'")
            val = str(val).replace('"',"\"")
            return val

def get_json_files(directory):
    json_files = []

    for subdir, dirs, files in os.walk(directory):
        for file in glob.glob(subdir + '/*.json'):
            json_files.append(file)

    return json_files


json_path = '/workspaces/chat-gpt-failures/datasets/galeras_curated_raw_V3/text-generation-inference'
json_files = get_json_files(json_path)

index = 338481
for i, file in enumerate(json_files):
    with open(file) as json_file:
        json_data = json.load(json_file)
        
        con = pymysql.connect(host = '192.168.0.1', port= 6603, user = 'galeras',passwd = 'galeras234',db = 'galeras')
        cursor = con.cursor()
        
        for j, item in enumerate(json_data):
            index += 1
            commit_id = item.get("commit_id")
            repo = item.get("repo")
            path= item.get("path")
            file_name = item.get("file_name")
            fun_name= item.get("fun_name")
            commit_message = item.get("commit_message")
            code =validate_string(item.get("code"))
            url = item.get("url")
            language = item.get("language")
            ast_errors= validate_string(''.join(item.get("ast_errors")))
            n_ast_errors= validate_string(item.get("n_ast_errors"))
            ast_levels= validate_string(item.get("ast_levels"))
            n_whitespaces= validate_string(item.get("n_whitespaces"))
            n_words= validate_string(item.get("n_words"))
            vocab_size= validate_string(item.get("vocab_size"))
            complexity= validate_string(item.get("complexity"))
            nloc=validate_string(item.get("nloc"))
            token_counts= validate_string(item.get("token_counts"))
            n_ast_nodes= validate_string(item.get("n_ast_nodes"))
            n_identifiers= validate_string(item.get("n_identifiers"))
            
            cursor.execute("INSERT INTO repo_code_dataset (id,commit_id,	repo,	path, file_name, fun_name, commit_message,\
                        code, url, language, ast_errors, n_ast_errors, ast_levels,n_whitespaces,n_words, vocab_size,complexity,\
                            nloc,token_counts,n_ast_nodes,n_identifiers)\
                            VALUES (%s,%s,	%s,	%s,%s,	%s,	%s,%s,	%s,	%s,%s,	%s,	%s,%s,	%s,	%s,%s,	%s,	%s,%s,	%s)",
                            (index, commit_id,	repo,	path, file_name, fun_name, commit_message,code, url, language,\
                                ast_errors, n_ast_errors, ast_levels,n_whitespaces,n_words,vocab_size,complexity,nloc,token_counts,n_ast_nodes,n_identifiers))
            documentation = item.get("documentation")
            if not documentation:
                continue
            docstring= documentation["docstring"]
            dn_words = validate_string(documentation["n_words"])
            d_vocab_size = validate_string(documentation["vocab_size"])
            dn_whitespaces = validate_string(documentation["n_whitespaces"])
            d_language = documentation["language"]
            
            cursor.execute("INSERT INTO repo_documentation (datapoint_id,docstring, n_words,vocab_size,n_whitespaces,language)\
                VALUES (%s,%s,%s,%s,%s,%s)",(index, docstring, dn_words,d_vocab_size,dn_whitespaces,d_language))
        con.commit()
        con.close()