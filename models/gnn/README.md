# Graph Neural Network (GNN) Models

This directory contains implementations and configurations for Graph Neural Network (GNN) models used in the OpenAuditLabs agent.

## Training Data Requirements

GNN models typically require structured graph data for training. This data should represent relationships and features relevant to the auditing tasks. Key aspects of the training data include:

- **Nodes:** Entities within the audit context (e.g., smart contract functions, variables, users).
- **Edges:** Relationships between these entities (e.g., function calls, data flow, access control).
- **Node/Edge Features:** Attributes associated with nodes and edges that the GNN can learn from (e.g., code properties, vulnerability indicators, historical data).

Training datasets are expected to be located in the `data/datasets` directory. Please refer to the specific model's documentation or configuration within this `models/gnn` directory for precise data formats and preprocessing steps.

## Model Assets

This directory will also house various assets related to the GNN models, such as:

- Pre-trained model weights.
- Model configuration files.
- Feature engineering scripts specific to GNNs.

## Data Sources

For information on available datasets and their structure, please refer to the main [data/datasets](../../data/datasets) directory.