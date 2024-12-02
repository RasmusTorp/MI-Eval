
import os
from omegaconf import OmegaConf
import wandb
import yaml

def wandb_init(config):

    try:
        with open("secret.txt", "r") as f:
            os.environ['WANDB_API_KEY'] = f.read().strip()
    
    except Exception as e:
        print(f"\nCreate a secret.txt file with you wandb API key {e}")
        return    
    
    print(f"configuration: \n {OmegaConf.to_yaml(config)}")
    # Initiate wandb logger
    try:
        # project is the name of the project in wandb, entity is the username
        # You can also add tags, group etc.
        run = wandb.init(project=config.training.wandb.project, 
                config=OmegaConf.to_container(config), 
                entity=config.training.wandb.entity)
        
        print(f"wandb initiated with run id: {run.id} and run name: {run.name}")
    except Exception as e:
        print(f"\nCould not initiate wandb logger\nError: {e}")
        
        
def get_target_config(config):
    
    def remove_value_keys(config):
        """Removes the 'value' key from each top-level key in the dictionary if it exists."""
        cleaned_config = {}
        for key, value in config.items():
            # If the current section has a 'value' key, use it; otherwise, keep it as is
            if isinstance(value, dict) and "value" in value:
                cleaned_config[key] = value["value"]
                
            else:
                cleaned_config[key] = value
                
        return cleaned_config
        
    api = wandb.Api()
    run = api.run(f"{config.training.wandb.entity}/{config.training.wandb.target_project}/{config.target_wandb_id}")
        
    # Download the YAML config file
    target_config = run.file("config.yaml").download(replace=True)
    print("Wandb config downloaded as 'config.yaml':")
    
    with open(target_config.name, 'r') as f:
        target_config_data = yaml.safe_load(f)
        print("Config contents:", target_config_data)
    
    target_config = remove_value_keys(target_config_data)
    target_config = OmegaConf.create(target_config)
    
    return target_config, run.name
    
def get_target_weights(target_config, attack_config):

    api = wandb.Api()
    run = api.run(f"{attack_config.training.wandb.entity}/{attack_config.training.wandb.target_project}/{attack_config.target_wandb_id}")
    if target_config.training.save_as:
        target_weights_filename = target_config.training.save_as
    else: # .pth filename is the same as wandb run name in this case
        target_weights_filename = run.name
    
    target_weights_path_wrapper = run.file(f"classifiers/saved_models/{target_weights_filename}.pth").download(replace=True)

    return target_weights_path_wrapper.name
