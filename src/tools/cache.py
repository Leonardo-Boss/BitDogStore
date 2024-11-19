import appdirs
import os
import json
import zipfile

user_data_dir = appdirs.user_data_dir("BitDogStore")
repositories = os.path.join(user_data_dir,'repositories')

def create_cache_dirs_if_not_exists():
    os.makedirs(user_data_dir, exist_ok=True)
    os.makedirs(repositories, exist_ok=True)
    
def extract_default_to_cache():
    if not ls_repos():
        file_path = os.path.realpath(__file__)
        file_path = file_path.removesuffix('/src/tools/cache.py')
        with zipfile.ZipFile(os.path.join(file_path,'default.zip'), 'r') as zip_ref:
            zip_ref.extractall(repositories)
        
def read_cache(name):
    if not os.path.exists(repositories):
        return None
    else:
        with open(name, "r") as file:
            data = file.read()
        return data

def ls_repos():
    return [os.path.join(repositories, filename) for filename in os.listdir(repositories)]

def get_repos_dir():
    return repositories