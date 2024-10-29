import os
import json

def get_apps_configs(dir: str):
    apps_configs = []
    assert "repo.json" in os.listdir(dir),"repo.json não encontrado"
    with open(f'{dir}/repo.json') as file:
        repo = json.load(file)
        
    assert "repository_name" in repo.keys(),"repo.json sem repository_name"
    assert "apps_folder" in repo.keys(),"repo.json sem apps_folder"
    for apps_folder in repo['apps_folder']:
        apps_dir = os.path.join(dir,apps_folder)
        assert os.path.exists(apps_dir),"diretorio de apps não encontrado"
        apps = os.listdir(apps_dir)
        for app in apps:
            path = os.path.join(apps_dir,app)
            if os.path.exists(os.path.join(path,'app.json')):
                with open(os.path.join(path,'app.json')) as file:
                    config = json.load(file)
                    if config.get('micropython_config'):
                        if not config['micropython_config'].get('firmware'):
                            if repo.get('repo_micropython_firmware'):
                                config['micropython_config']['firmware'] = os.path.join(path,repo['repo_micropython_firmware'])
                            else:
                                config['micropython_config']['firmware'] = os.path.join(
                                    os.path.abspath(os.getcwd()),'default.uf2')
                        else:
                            config['micropython_config']['firmware'] = os.path.join(path,config['micropython_config']['firmware'])
                        for i,file in enumerate(config['micropython_config']['files']):
                            config['micropython_config']['files'][i] =  os.path.join(path,file)
                    else:
                        config['c_config']['firmware'] = os.path.join(path,config['c_config']['firmware'])
                    if config.get('app_page_docs'):
                        config['app_page_docs'] = os.path.join(path,config['app_page_docs'])
                    apps_configs.append(config)
            config = None
        apps = None
    return apps_configs

print(get_apps_configs('/home/eduardo/Desktop/Projetos_Disciplina_IE323'))