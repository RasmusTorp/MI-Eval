# MI-Eval: Re-thinking Defense Application and Evaluation for Model Inversion

MI-Eval is a collection of tools for researching model inversion attacks and defenses for deep classification models.

### Disclaimer
This repository is still in alpha. More testing will be done, and additional features will be coming soon, marked by: *

## Table of Contents
- [Installation and setup](#installation-and-setup)
- [Features](#features)
- [Usage](#usage)

## Installation and setup

Since this repository relies on other researchers code for defenses and attacks, it clones several other repos into the repository. However, this process has been streamlined using bash scripts. To setup the repo, 

### Steps
1. Clone the repository.
2. Setup and activate environment. The repository is devolped to Python 3.11. Eg using conda:
```
conda create -n ENVIRONMENT_NAME python=3.11
```
3. Install dependencies.
```
pip install -r requirements.txt
pip install torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cu121
```
4. Run bash script for setting up other repositories and downloading pretrained GAN's.
```
bash setup_files.bash
```
5. Weights and Biases Logging (Optional, but recommended).
   - Setup Weights and Biases account: https://wandb.ai/site/
   - Create a project.
   - Get the API key and make a file "secret.txt" in the main scope of the repository.
   - Set the entity and project names in the configuration (configuration/classifier/training/default.yaml and configuration/model_inversion/training/default.yaml respectively)
   - Run scripts with training.wandb.track=True in the command or set it as default in the configuration.
   - Enjoy smart and scalable cloud logging for training classifiers and model inversion. 🚀 

## Features
This section will go present the different defenses, attacks and dataset that this repository will support. To see some examples, this [wandb report](https://api.wandb.ai/links/BreuerLab/rbbr8jqr) contains results from running a Plug-and-Play attack on various model defenses, with some additional insights into the training of target models.

### Defenses
| Name | Citation | Implementation | Command (defense=) | 
|----------|----------|---------|---------|
| TL-DMI     | [Ho et al. 2024](https://arxiv.org/abs/2405.05588) | [Github](https://github.com/hosytuyen/TL-DMI) | tldmi
| Neg-LS     | [Struppek et al. 2024](https://arxiv.org/abs/2310.06549)   | [Github](https://github.com/LukasStruppek/Plug-and-Play-Attacks) | label_smoothing
| BiDO       | [Peng et al. 2022](https://arxiv.org/abs/2206.05483)   | [Github](https://github.com/AlanPeng0897/Defend_MI) | bido
| MID        | [Wang et al. 2020](https://arxiv.org/abs/2009.05241) | [Github](https://github.com/Jiachen-T-Wang/mi-defense) | mid

### Attacks
| Name | Resolution | Citation | Implementation | Command (attack=) | 
|----------|----------|---------|---------| ---------|
| PPA          | High-Res | [Struppek et al. 2022](https://proceedings.mlr.press/v162/struppek22a.html) | [Github](https://github.com/LukasStruppek/Plug-and-Play-Attacks) | plug_and_play
| PLG-MI * | High-Res | [Yuan et al. 2023](https://arxiv.org/abs/2302.09814)   | [Github](https://github.com/LetheSec/PLG-MI-Attack) | plg_mi
| IF-GMI * | High-Res | [Qiu et al. 2024](https://arxiv.org/abs/2407.13863) | [Github](https://github.com/final-solution/IF-GMI) | if_gmi
| KED-MI * | High-Res | [Chen et al. 2021](https://arxiv.org/abs/2010.04092) | [Github](https://github.com/SCccc21/Knowledge-Enriched-DMI) | ked_mi

### Classifiers

We support a simple MLP and CNN implementation and a range of pretrained classifiers from torchvision including: (ResNet18, Resnet152, Inceptionv3). 

A custom classifier or defenses can also be tested by implementing CustomClassifier in custom_classifier.py and running model=custom in the command line. Parameters for this can be added at will in configuration/classifier/custom.yaml. 


### Datasets
Most of the datasets are implemented with automatic downloading and processing. 

| Name | Size | Resolution | Downloading |
|----------|----------|---------|---------|
| Facescrub     | 141,130 |  High-Res  | Automatic  |
| Standord Dogs | 20,580  |  High-Res  | Automatic  |
| CelebA        | 202,599 |  High-Res  | Automatic* |
| CIFAR10       | 60.000  |  Low-Res   | Automatic  |
| MNIST         | 60.000  |  Low-Res   | Automatic  |
| FashionMNIST  | 60.000  |  Low-Res   | Automatic  |

(*) There is a bug at the moment with downloading CelebA with gdown (Download img_align_celeba.zip and put in the data/celeba from the link and unzip: https://drive.google.com/drive/folders/0B7EVK8r0v71pWEZsZE9oNnFzTm8?resourcekey=0-5BR16BdXnb8hVj6CNHKzLg)

## Usage
The repository utilizes hydra for dynamic hierachical configuration (https://hydra.cc/docs/intro/). The default parameters can be changed in the configuration folder or via the hydra CLI syntax.

### Training Classifiers
It easy to shift between datasets and models in the command line as such:
```
python train_classifier.py dataset=CelebA model=pretrained model.architecture="ResNet152" model.hyper.epochs=50 training.wandb.track=True
```

### Defending Classifiers
To defend classifiers, simply add the defense in the command for training classifiers:

```
python train_classifier.py defense=tldmi dataset=CelebA model=pretrained model.architecture="ResNet18" training.wandb.track=True
```

### Attacking Classifiers
Attacking classifiers can be done configured similarly:
```
python run_model_inversion.py dataset=FaceScrub attack=plug_and_play target_wandb_id="TARGET_RUN_ID" attack.evaluation_model.wandb_id="EVAL_RUN_ID" training.wandb.track=True
```
