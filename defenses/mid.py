import torchvision
import torch.nn as nn
import torch
import torch.nn.functional as F

from classifiers.abstract_classifier import AbstractClassifier

def apply_MID_defense(config, model:AbstractClassifier):
    
    class MID(model.__class__):
            
        def __init__(self, config):
            super(MID, self).__init__(config)            
            list_of_layers = list(self.model.children())
            last_layer = list_of_layers[-1]
            # self.feat_dim = 512 * 2 * 2
            self.feat_dim = last_layer.in_features
            self.k = self.feat_dim // 2
            self.n_classes = config.dataset.n_classes
            
            self.model.fc = nn.Identity() # removes final classification layer
            
            self.st_layer = nn.Linear(self.feat_dim, self.k * 2)
            self.fc_layer = nn.Linear(self.k, self.n_classes)
            
        def forward(self, x, mode="train"):
            feature = self.model(x)

            feature = feature.view(feature.size(0), -1)
            
            statis = self.st_layer(feature)
            
            mu, std = statis[:, :self.k], statis[:, self.k:]
            
            std = F.softplus(std-5, beta=1) #! Parameters?
            eps = torch.FloatTensor(std.size()).normal_().to(self.device)
            res = mu + std * eps
            out = self.fc_layer(res)
            
            __, iden = torch.max(out, dim=1)
            iden = iden.view(-1, 1)
        
            return [feature, mu, std, out]

        def forward_only_logits(self, x):
            ___, ___, ___, out = self(x)
            return out
        
        def save_model(self, name):
            path = f"classifiers/saved_models/{name}"
            if isinstance(self.model, nn.DataParallel): # self.model, self.st_layer, and self.fc_layer are on DataParallel
                state = {
                    "model": self.model.module.state_dict(),
                    "st_layer": self.st_layer.module.state_dict(),
                    "fc_layer": self.fc_layer.module.state_dict(),
                }
            else:
                state= {
                    "model": self.model.state_dict(),
                    "st_layer": self.st_layer.state_dict(),
                    "fc_layer": self.fc_layer.state_dict(),
                }
            torch.save(state, path)


        def load_model(self, file_path, map_location = None):
            if map_location is None:
                state = torch.load(file_path, weights_only=True)
            else:
                state = torch.load(file_path, map_location=map_location, weights_only=True)  

            if isinstance(self.model, nn.DataParallel):
                self.model.module.load_state_dict(state['model'])
                self.st_layer.module.load_state_dict(state['st_layer'])
                self.fc_layer.module.load_state_dict(state['fc_layer'])
            else:
                self.model.load_state_dict(state['model'])
                self.st_layer.load_state_dict(state['st_layer'])
                self.fc_layer.load_state_dict(state['fc_layer'])


        
        def predict(self, x):
            feature, mu, std, out = self(x)
            
            out = torch.argmax(out, dim=1)
        
            return out

        def debug_forward(self, dataloader):
            self.to(self.device)
            dataset = dataloader.dataset
            x, y = dataset[0]
            x = x.to(self.device)
            
            x = x.unsqueeze(0)
            
            feature, mu, std, out = self(x)
            
            return [feature, mu, std, out]


        def train_model(self, train_loader, val_loader):
            if torch.cuda.device_count() > 1:
                self.st_layer = nn.DataParallel(self.st_layer) # self.model will be put on DataParallel in super train_model call, so we just need to put the st_layer on DataParallel here
                self.fc_layer = nn.DataParallel(self.fc_layer) # self.model will be put on DataParallel in super train_model call, so we just need to put the fc_layer on DataParallel here

            return super(MID, self).train_model(train_loader, val_loader)
        

        def get_loss(self, output, target):
            ___, mu, std, out_prob = output
            cross_loss = self.criterionSum(out_prob, target)
            info_loss = - 0.5 * (1 + 2 * std.log() - mu.pow(2) - std.pow(2)).sum(dim=1).sum()
            loss = cross_loss + self.config.defense.beta * info_loss
        
            return loss
        
        def evaluate(self, loader):
            self.to(self.device)
            self.eval()
            
            correct = 0
            total_loss = 0
            total_instances = 0
            
            with torch.no_grad():
                for batch_idx, (data, target) in enumerate(loader):
                    data, target = data.to(self.device), target.to(self.device)
                    output = self(data)

                    loss = self.get_loss(output, target)

                    total_loss += loss.item()
                    
                    total_instances += len(data)
                    
                    _, _, _, out = output #! This is the change
                    
                    pred = torch.argmax(out, dim=1)
                    correct += (pred == target).sum().item()
            
            avg_loss = total_loss / total_instances
            accuracy = correct / total_instances
            
            return avg_loss, accuracy
            
    protected_model = MID(config)
    
    return protected_model
