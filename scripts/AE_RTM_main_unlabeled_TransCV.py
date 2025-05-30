import sys
import os
import warnings
warnings.filterwarnings('ignore')  # ignore warnings, like ZeroDivision

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

os.getcwd()

from src.utils_data import *
from src.transformation_utils import *
from src.utils_all import *

#### Model definition ###
from src.rtm_torch.Resources.PROSAIL.call_model import *
from src.AE_RTM.AE_RTM_architectures import *
from src.AE_RTM.trainer_ae_rtm import *

from itertools import islice

import glob
import gc

import pandas as pd
import wandb 
import torch
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split

############
import argparse

# Create the parser
my_parser = argparse.ArgumentParser(description='Training semi-supervised method')

# Add the arguments
my_parser.add_argument('--seed',
                       metavar='seed',
                       type=int,default=155,
                       help='SEED')

my_parser.add_argument('--path_data_lb',
                       metavar='path_data_lb',
                       default=str(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),  'Datasets/50_all_traits.csv')),
                       type=str,
                       help='Path the labeled data')

my_parser.add_argument('--directory_path',
                       metavar='directory_path',
                       default=str(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),  'Splits')),
                       type=str,
                       help='Path the unlabeled splits')

my_parser.add_argument('--path_save',
                       metavar='path_save',
                       default=str(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),  '/ae_rtm')),
                       type=str,
                       help='the path to checkpoint and metadata')


my_parser.add_argument('--input_shape',
                       metavar='input_shape',
                       type=int,default=1721,
                       help='input_shape AE_RTM')

my_parser.add_argument('--type_s',
                       metavar='type_s',
                       type=str,default='full',
                       help='Type of the sensor: full OR half range')


my_parser.add_argument('--n_epochs',
                       metavar='n_epochs',
                       type=int,default=500,
                       help='Number of epochs')

my_parser.add_argument('--batch_size',
                       metavar='batch_size',
                       type=int,default=128,
                       help='batch_size')


my_parser.add_argument('--lr',
                       metavar='lr',
                       type=float,default=1e-3,
                       help='Learning rate')

my_parser.add_argument('--name_experiment',
                       metavar='name_experiment',
                       type=str,default='',
                       help='name_experiment')


my_parser.add_argument('--project_wandb',
                       metavar='project_wandb',
                       type=str,default='',
                       help='project_wandb')



# Execute the parse_args() method
args = my_parser.parse_args()

path_save = args.path_save ##path_save
project = args.project_wandb ## experiment name 

directory_path = args.directory_path
path_data_lb = args.path_data_lb

seed = args.seed

batch_size = args.batch_size 
n_epochs = args.n_epochs
lr = args.lr
name_experiment = args.name_experiment ## experiment name 


input_shape = args.input_shape
type_s = args.type_s

###############

# Check if GPU is available
if torch.cuda.is_available():
    # Set the device to GPU
    device = torch.device("cuda")
    print("GPU is available. Using GPU for computation.")
else:
    # If GPU is not available, fall back to CPU
    device = torch.device("cpu")
    print("GPU is not available. Using CPU for computation.")

from datetime import datetime

# Get the current date and time
current_datetime = datetime.now()

# Format the date and time in YYMMDD_HHMM format
formatted_datetime = current_datetime.strftime("%y%m%d_%H%M")

ls_tr = ["cab", "cw", "cm", "LAI", "cp", "cbc", "car", "anth"]


percentage_tr = 1

######## Data ########
file_paths = glob.glob(os.path.join(directory_path, "*.csv"))

################ Lbeled ###############
db_lb = pd.read_csv(path_data_lb, low_memory=False).drop(['Unnamed: 0'], axis=1)

if __name__ == "__main__":
    seed_all(seed=seed)

    for i, (db_lb_all, samples_val_ext, test_ids) in islice(enumerate(sliding_custom_cv(db_lb, seed=42)), 0, None):
        run = 'AE_RTM_{}_gp{}UNlabels_{}'.format(formatted_datetime, i, seed)
        checkpoint_dir = os.path.join(path_save, "checkpoints_{}".format(run)) #'./checkpoints'

        if not os.path.exists(path_save):
            os.mkdir(path_save)

        if not os.path.exists(checkpoint_dir):
            os.mkdir(checkpoint_dir)
        
        # Optional: Summarize GPU memory usage
        print(torch.cuda.memory_summary())

        X_labeled, y_labeled = data_prep_db(db_lb_all, ls_tr)
        metadata = db_lb_all.iloc[:, :1]  # The metadata (dataset of origin)
        
        
        red_ed = X_labeled.loc[:,750]
        red_end = X_labeled.loc[:,1300]
        red1000_ = X_labeled.loc[:,1000]
        
        idx = X_labeled[(red_end>red1000_) & (red_ed>red1000_)].index
        
        if(len(idx)>0):
            X_labeled.drop(idx, inplace=True)
            y_labeled.drop(idx, inplace=True)
            metadata.drop(idx, inplace=True)
        
        
        # Split labeled data into train (80%), validation (20%)
        X_train, X_val= train_test_split(X_labeled, test_size=0.2, stratify=metadata.dataset, random_state=300)
        
        y_train = y_labeled.loc[X_train.index,:]
        y_val = y_labeled.loc[X_val.index,:]
        
        meta_train = metadata.loc[X_train.index,:]
        meta_val = metadata.loc[X_val.index,:]
        
        
        ### external
        ext_val_x, ext_val_y = data_prep_db(samples_val_ext, ls_tr)
        meta_ext = samples_val_ext.iloc[:, :1]

        
        ########## Scaler ###
        scaler_list = save_scaler(y_train, standardize=True, scale=True, save=True, dir_n=checkpoint_dir, k='all_{}'.format(100*percentage_tr))
        
        # Create the dataset
        train_dataset = SpectraDataset(X_train, y_train, meta_train, augmentation=True, aug_prob=0.8)
        # Define DataLoader with the custom collate function for fair upsampling
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        test_dataset = SpectraDataset(X_train=X_val, y_train=y_val, meta_train=meta_val, augmentation=False)
        # Create DataLoader for the test dataset
        valid_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        
        # # Create the dataset
        untrain_dataset = MultiFileAugmentedCSVDataset(file_paths, chunk_size=1000, augmentation=True, aug_prob=0.5, scale=False) ## No scaling of spectra
        unlabeled_loader = DataLoader(untrain_dataset, batch_size=batch_size, 
                                shuffle=True
                            )

        test_dataset_ext = SpectraDataset(X_train=ext_val_x, y_train=ext_val_y, meta_train=meta_ext, augmentation=False)
        # Create DataLoader for the test dataset
        ext_loader = DataLoader(test_dataset_ext, batch_size=batch_size, shuffle=False)
        
        ######
        # Example usage:
        settings_dict = {
            'epochs': n_epochs,
            'train_loader': train_loader,
            'unlabeled_loader' : unlabeled_loader,
            'valid_loader': valid_loader,
            'checkpoint_dir': checkpoint_dir,
            'batch_size': batch_size,
            'learning_rate': lr,
            'weight_decay' : 1e-5,
            'early_stop': True,
            'patience': 10,
            'scaler_model': scaler_list,
            'input_shape' : input_shape, #500, #1721,
            'type':type_s,
            'log_epoch' : 10,
            'lamb': 1e0,
            'loss_recons_criterion': CosineSimilarityLoss(), #CosineSimilarityLoss() #mse_loss
            # 'logger': wandb
        }
        
        # ### with wandb #####
        # wandb.init(
        #     # Set the project where this run will be logged
        #     project=project,
        #     # We pass a run name (otherwise it’ll be randomly assigned, like sunshine-lollypop-10)
        #     name=f"experiment_{run}",
        #     # Track hyperparameters and run metadata
        #     config=settings_dict,      # Log the configuration parameters.
        #     dir= checkpoint_dir
        #     )
        
        #>>> Model input 1721 !!!
        
        sets = Settings_ae()
        sets.update_from_dict(settings_dict)
        
        test_reg = Trainer_AE_RTM(sets)
        # test_reg.settings.logger = wandb  # Attach wandb logger to the trainer.

        test_reg.train()
        
        if (test_reg.settings.logger is not None):
            test_reg.settings.logger.finish() 

        ##############
        preds = torch.empty(0,8).to(device)
        ori = torch.empty(0,8).to(device)
        test_reg.model.eval()
        
        with torch.no_grad():
            for batch_idx, val_sample in enumerate(ext_loader): #
                data_val, lb_bx_val, _ = val_sample
                
                lb_bx_val = lb_bx_val.to(device).float()
                data_val = data_val.squeeze().float().to(device)
                
                x_val, _ = test_reg.model(data_val)
                        
                ori = torch.cat((ori.data,lb_bx_val.data), dim=0)
                preds = torch.cat((preds.data,x_val[:,:].data), dim=0)
        
        
        if(test_reg.settings.scaler_model is not None):
            preds = test_reg.transformation_layer_inv(preds) ### shoud keep the sam eorder of labels !!!
            
        ori_lb = pd.DataFrame(ori.cpu(), columns=ls_tr[:])
        df_tr_val = pd.DataFrame(preds.cpu(), columns=ls_tr[:])
        df_tr_val['cbc'] = df_tr_val['cm']-df_tr_val['cp']

        ori_lb.to_csv(os.path.join(checkpoint_dir, "Obs_CV{}.csv".format(i)))
        df_tr_val.to_csv(os.path.join(checkpoint_dir, "Preds_CV{}.csv".format(i)))
        
        val_mertics = eval_metrics(ori_lb, df_tr_val)
        val_mertics.to_csv(os.path.join(checkpoint_dir, "ValidationMetrics_CV{}.csv".format(i)))
        
        # Clean up after training
        del test_reg
        gc.collect()
        torch.cuda.empty_cache()
        
        print(f"Completed training model {percentage_tr}. GPU memory cleared.\n")