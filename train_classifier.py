from omegaconf import OmegaConf
import hydra
import wandb
import os
import torch

from data_processing.data_loaders import get_data_loaders
from classifiers.get_model import get_model

@hydra.main(config_path="configuration/classifier", config_name="config.yaml", version_base="1.3")
def train_classifier(config):

    if config.training.wandb.track:
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
            
    # Load the data
    train_loader, val_loader, test_loader = get_data_loaders(config)
    
    model = get_model(config)
    
    model.train_model(train_loader, val_loader)
    
    test_loss, test_accuracy = model.evaluate(test_loader)
    
    if config.training.wandb.track:
        wandb.log({"test_loss": test_loss})
        wandb.log({"test_accuracy": test_accuracy})
    
    
if __name__ == "__main__":
    train_classifier()