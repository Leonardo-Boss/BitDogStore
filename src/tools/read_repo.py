import os
import json
# TODO: usar path.join

def get_apps_configs(DIR: str):
    apps_configs = []
    assert "repo.json" in os.listdir(DIR),"repo.json não encontrado"
    with open(f'{DIR}/repo.json') as file:
        repo = json.load(file)
        
    assert "repository_name" in repo.keys(),"repo.json sem repository_name"
    assert "apps_folder" in repo.keys(),"repo.json sem apps_folder"
    for i in repo['apps_folder']:
        assert os.path.exists(f'{DIR}/{i}'),"diretorio de apps não encontrado"
        apps = os.listdir(f'{DIR}/{i}')
        for app in apps:
            if os.path.exists(f'{DIR}/{i}/{app}/app.json'):
                with open(f'{DIR}/{i}/{app}/app.json') as file:
                    config = json.load(file)
                    config["path"] = f'{DIR}/{i}/{app}'
                    apps_configs.append(config)
            config = None
        apps = None
    return apps_configs
