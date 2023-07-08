from pydriller import Repository
from datetime import datetime
import re
import json
import os
import cld3

import ast_tree
from tree_sitter import Language, Parser
import list_all_repos

start_date = datetime(2022, 1, 1, 0, 0, 0)
end_date = datetime(2023, 1, 1, 0, 0, 0)

# Then query for Python repositories sorted by stars and exclude forks
query = 'language:Python fork:false pushed:>2021-12-31 stars:>1000 org:facebook'
#'language:Python fork:false size:>=30000 pushed:>2021-12-31 stars:>2000'

repos = list_all_repos.get_all_repos(query, 200)
methods = ()
save_path = "/nfs/semeru/semeru_datasets/galeras_curated_raw_V3/{}/{}"
save_path1 = "/nfs/semeru/semeru_datasets/galeras_curated_raw_V3/{}"


#'/scratch/danielrc/dataset_extractor/repos/{}'.format(repo_name)
# repo: the owner/repo
# path: the full path to the original file
# func_name: the function or method name
# original_string: the raw string before tokenization or parsing
# language: the programming language
# code/function: the part of the original_string that is code
# code_tokens/function_tokens: tokenized version of code
# docstring: the top-level comment or docstring, if it exists in the original string
# docstring_tokens: tokenized version of docstring
# url: the url for the example (identify natural language)
# idx: the index of code (identify code)





class TreeSitterManager():
    def __init__(self, lang):
        self.language = self.get_language(lang)
        self.parser = Parser()
        self.parser.set_language(self.language)

    def get_language(self, lang):
        return Language(f"{ast_tree.__path__[0]}/grammars/tree-sitter-languages.so", lang)

    def get_ast_errors_and_deep(self, code):
        node_tree = self.parser.parse(bytes(code, "utf8"))
        return self.__detect_ast_errors_and_deep(node_tree.root_node, set())

    def __detect_ast_errors_and_deep(self, node_root, identifier_set = set(), level=0, max_level=0, count = 0):
        """Traverses the tree catch errors and evaluate tree levels"""
        # if not node_root.has_error:
        #     return [], 0
        counter = node_root.child_count

        results = []
        if node_root.type == "ERROR":
            results.append(node_root.text.decode("utf-8"))
        elif node_root.type == "identifier":
            identifier_set.add(node_root.text)
        level += 1
        for n in node_root.children:
            x, identifier_set, y, max_level, count = self.__detect_ast_errors_and_deep(n, identifier_set, level, max_level)
            max_level = max(y, max_level)
            counter += count
            if len(x) > 0:
                results.extend(x)

        return results, identifier_set, max_level, level, counter

class GithubMiningManager():
    
    def __init__(self,repo_name):
        self.ast_error_detector = TreeSitterManager("python")
        self.repo_name = repo_name

    def extract_methods(self,source_code, methods):
        regex = r"(\n(\s{4})*)(def |class |async |    @[a-zA-Z]*)"  # r"\n(def |[ {4}]*def |class |    @[a-zA-Z]*)"
        if source_code is None:
            return
        search = re.finditer(regex, source_code, flags=re.MULTILINE)
        start_index = 0
        index_line = {}
        counter = 0
        for s in search:
            if start_index == 0:
                start_index = s.start() + 1
                code = source_code[:start_index]
                counter = len(re.findall("\n", code)) + 1
                continue
            code = source_code[start_index:s.start()]
            index_line[str(counter)] = code.lstrip()
            counter = counter + len(re.findall("\n", code)) + 1
            start_index = s.start() + 1
        code = source_code[start_index:]
        index_line[str(counter)] = code.lstrip()

        list_filtered_methods = []
        for n in methods:
            try:
                final_method = index_line[str(n.start_line)]
                if n.long_name.replace(" ", "") in final_method.split(":")[0].replace(" ", ""):
                    ast_errors, identifier_set, ast_deep, level, count = self.ast_error_detector.get_ast_errors_and_deep(final_method)
                    list_filtered_methods.append((n.name, final_method, ast_errors, n.complexity, n.nloc, n.token_count, ast_deep, count, identifier_set))
                elif n.long_name in source_code:
                    '''Confirm method does not exist:'''
                    print("method exists but failed to recover")
            except KeyError:
                continue

        return list_filtered_methods


    def create_json(self,hash, repo, path, file_name, func_name, commit_message, code, documentation, url, language, ast_errors,
                    complexity, nloc, tokens, ast_deep, ast_node_count, identifiers ):
        words = code.split()
        return {"commit_id": hash,
                "repo": repo, 
                "path": path, 
                "file_name": file_name, 
                "fun_name": func_name,
                "commit_message": commit_message, 
                "code": code, 
                "documentation": documentation,
                "url": url, 
                "language": language, 
                "ast_errors": ast_errors,
                "n_ast_errors": len(ast_errors), 
                "ast_levels": ast_deep,
                "n_whitespaces": code.count(' '),
                "n_words": len(words),
                "vocab_size": len(set(words)),
                "complexity": complexity,
                "nloc": nloc,
                "token_counts": tokens,
                "n_ast_nodes": ast_node_count,
                "n_identifiers": len(identifiers)
                }


    def split_code_docstring(self,original_code):
        regex = "(\"\"\"|\'\'\')"
        if re.search(regex, original_code) is None:
            return None, original_code
        split = re.split(regex, original_code)
        code = ""
        doc_string = ""
        is_doc = False
        for text in split:
            is_comment = re.search(regex, text) is not None
            is_doc = is_comment != is_doc
            if is_comment:
                continue
            if is_doc:
                doc_string = doc_string + re.sub(regex, "", text)
            else:
                code = code + text

        return doc_string, code




    def save(self, name, data):           
        if not os.path.exists(save_path1.format(self.repo_name)):
            os.mkdir(save_path1.format(self.repo_name))
        with open(save_path.format(self.repo_name,name), 'w') as f:
            print("saving data")
            json.dump(data, f, ensure_ascii=False, indent=4)
            
    def documentation_object(self,docstring):
        lan = cld3.get_language(docstring)
        if docstring is None:
            return {}
        words = docstring.split()
        language = lan.language
        if lan.probability < 0.9: #not reliable
            language ="UNKNOWN"
        return {"docstring": docstring, "n_words":len(words), "vocab_size":len(set(words)), "n_whitespaces": docstring.count(' '), "language": language}


    def manage_commits(self, commits):
        json_list = []
        counter = 0
        data_files = 1
        try:
            for commit in commits:
                
                for file in commit.modified_files:
                    if not file.filename.endswith('.py'):
                        continue
                    methods = self.extract_methods(file.source_code, file.changed_methods)
                    if methods is None:
                        continue

                    for method in methods:
                        docstring, actual_code = self.split_code_docstring(method[1])
                        json_method = self.create_json(commit.hash, commit.project_name, file.new_path, file.filename, method[0], commit.msg,
                                                actual_code, self.documentation_object(docstring), remote_repo_path, "Python", method[2], method[3],
                                                method[4], method[5], method[6],method[7],method[8])
                        json_list.append(json_method)
                    if len(json_list) > 5000:
                        self.save("data_{}.json".format(str(data_files)), json_list)
                        data_files = data_files + 1
                        json_list = []
            
        except Exception as inst:
            print("missed commit error" )
            self.save("data_{}.json".format(str(data_files)), json_list)
        if len(json_list)>0:
            self.save("data_{}.json".format(str(data_files)), json_list)
        print(len(json_list))
    


for repo in repos:
    
    repo_name =  repo[0]
    remote_repo_path = repo[1]
    commits = Repository(remote_repo_path, since=start_date, to=end_date, only_no_merge = True,
                        only_modifications_with_file_types=['.py'], only_in_branch=repo[2]).traverse_commits()
    print("starting mining ", repo_name)
    miner = GithubMiningManager(repo_name)
    miner.manage_commits(commits)

#save("data_{}.json".format(str(data_files)), json_list)


##git config --global -add safe.directory
