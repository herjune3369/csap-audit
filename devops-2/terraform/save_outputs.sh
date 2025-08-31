#!/bin/bash
# Create ansible directory if it doesn't exist
mkdir -p ../ansible

# Save terraform outputs to JSON file
terraform output -json > ../ansible/terraform_outputs.json

echo "✅ Terraform outputs saved to ../ansible/terraform_outputs.json" 