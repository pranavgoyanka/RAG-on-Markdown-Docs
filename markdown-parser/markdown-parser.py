import markdown_to_json
import pprint

with open('../data/OmniFlow.md', 'r') as file:
    data = file.read()
    
# print(data)

md_dict = markdown_to_json.dictify(data)

# pprint.pprint(md_dict)

# DFS into the dictionary 
# start from the first set of keys?
# this is very rudamentary and contains 
# repititions in the order of the nesting level
# TODO: refine this to decrease repititions
def dfs_dict(d, path):
    if path is None:
        path = []
        
    for key, value in d.items():
        path.append({"key": key, "value": value})
        
        if isinstance(value, dict):
            # Recursively apply DFS if the value is another dictionary
            dfs_dict(value, path)

all_data = []        
dfs_dict(md_dict, all_data)

pprint.pprint(all_data)
