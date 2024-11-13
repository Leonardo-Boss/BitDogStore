import appdirs
import os
import json

user_data_dir = appdirs.user_data_dir("BitDogStore")
repositories = os.path.join(user_data_dir,'repositories')

def create_cache(name,data):
    os.makedirs(user_data_dir, exist_ok=True)
    os.makedirs(repositories, exist_ok=True)
    
    with open(name, "w") as file:
        file.write(data)
    
    print("file saved")

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