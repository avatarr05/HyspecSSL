# README

# 🌱 Semi-Supervised Learning for Hyperspectral Data

This repository contains a collection of training scripts and experiments for semi-supervised learning on hyperspectral reflectance data. It includes implementations of various models such as MAE (Masked Autoencoders), GANs, Autoencoders (AE-RTM), and a Multi-trait learning framework.

The aim is to evaluate and compare different semi-supervised strategies on spectral datasets. All training scripts are located in the `scripts/` directory and are meant to be executed via command-line with custom arguments.

## 📁 Project Structure

```
.
├── scripts/
│   ├── mae_Reg_main_unlabeled.py
│   ├── Gan_main_unlabeled.py
│   ├── AE_RTM_main.py
│   ├── AE_RTM_main_unlabeled.py
│   └── multi_main.py
    └── Split_data.py
├── Datasets/
├── Splits/
├── README.md
└── requirements.txt
```

## 🥪 Requirements

- Python 3.8+
- PyTorch
- NumPy
- Pandas
- wandb (optional for experiment tracking)

To install the dependencies:

```bash
pip install -r requirements.txt
```

## 🚀 Running the Scripts

All scripts accept CLI arguments and are designed for flexible experimentation. Below are the commands to run each training pipeline.

### 🔷 MAE (Masked Autoencoder)

\`\`\`bash
python scripts/mae_Reg_main_unlabeled.py \
  --seed 155 \
  --path_data_lb /path/to/your_dataset.csv \
  --directory_path /path/to/Splits \
  --input_shape 1720 \
  --type_s full \
  --n_epochs 1 \
  --name_experiment Test_Un100 \
  --path_save /path/to/output/mae_model/ \
  --mask_ratio 0.75
\`\`\`

### 🔶 SR-GAN

\`\`\`bash
python scripts/Gan_main_unlabeled.py \
  --seed 155 \
  --path_data_lb /path/to/your_dataset.csv \
  --directory_path /path/to/Splits \
  --input_shape 1720 \
  --type_s full \
  --n_epochs 1 \
  --name_experiment Test_Un100 \
  --path_save /path/to/output/gan_model/
\`\`\`

### 🟩 RTM-AE (Labeled)

\`\`\`bash
python scripts/AE_RTM_main.py \
  --seed 155 \
  --path_data_lb /path/to/your_dataset.csv \
  --directory_path /path/to/Splits \
  --input_shape 1721 \
  --type_s full \
  --n_epochs 1 \
  --batch_size 128 \
  --lr 1e-3 \
  --name_experiment Test_Un100 \
  --project_wandb rtm_py_withScaler \
  --path_save /path/to/output/ae_rtm/
\`\`\`

### 🟧 RTM-AE (Unlabeled)

\`\`\`bash
python scripts/AE_RTM_main_unlabeled.py \
  --seed 155 \
  --path_data_lb /path/to/your_dataset.csv \
  --directory_path /path/to/Splits \
  --input_shape 1721 \
  --type_s full \
  --n_epochs 1 \
  --batch_size 128 \
  --lr 1e-3 \
  --name_experiment Test_Un100 \
  --project_wandb rtm_py_withScaler \
  --path_save /path/to/output/ae_rtm/
\`\`\`

### 🟨 Multi-trait Model

\`\`\`bash
python scripts/multi_main.py \
  --seed 155 \
  --path_data_lb /path/to/your_dataset.csv \
  --directory_path /path/to/Splits \
  --input_shape 1720 \
  --type_s full \
  --n_epochs 1 \
  --name_experiment Test_Un100 \
  --path_save /path/to/output/multi-trait_model/
\`\`\`

## 📊 CLI Argument Descriptions

- \`--seed\`: Random seed for reproducibility
- \`--path_data_lb\`: Path to the labeled dataset CSV file
- \`--directory_path\`: Path to the folder containing split CSV files
- \`--input_shape\`: Number of input features (e.g. 1720 or 1721)
- \`--type_s\`: Training subset type (e.g. \`full\`)
- \`--n_epochs\`: Number of training epochs
- \`--batch_size\`: Batch size for training (if applicable)
- \`--lr\`: Learning rate (if applicable)
- \`--mask_ratio\`: Ratio of features to mask (for MAE only)
- \`--name_experiment\`: Name/identifier for the current experiment
- \`--project_wandb\`: Name of the Weights & Biases project (optional)
- \`--path_save\`: Directory to save model outputs, logs, etc.

## 📂 Outputs

Each script will:
- Train the selected model architecture
- Save experiment outputs under the provided \`--path_save\`
- Optionally log training progress and metrics to Weights & Biases

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more information.
