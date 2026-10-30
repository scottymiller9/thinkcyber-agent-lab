#!/usr/bin/env bash
# Stand up a Microsoft Foundry (Azure OpenAI) resource and deploy gpt-5-mini.
# The portal is honestly easier for this; this script is the CLI equivalent.
# After it runs, copy the endpoint + key into your .env.
set -euo pipefail

RG="rg-pentest-workshop"
LOCATION="eastus"
ACCOUNT="foundry-pentest-$RANDOM"
DEPLOYMENT="gpt-5-mini"
MODEL="gpt-5-mini"          # change if a newer mini is current in your region
MODEL_VERSION=""            # leave blank to let Azure pick the default version

echo ">> Azure OpenAI / Foundry account"
az cognitiveservices account create \
  -n "$ACCOUNT" -g "$RG" -l "$LOCATION" \
  --kind OpenAI --sku S0 --yes -o none

echo ">> Model deployment: $DEPLOYMENT ($MODEL)"
az cognitiveservices account deployment create \
  -n "$ACCOUNT" -g "$RG" \
  --deployment-name "$DEPLOYMENT" \
  --model-name "$MODEL" \
  ${MODEL_VERSION:+--model-version "$MODEL_VERSION"} \
  --model-format OpenAI \
  --sku-capacity 20 --sku-name Standard -o none

ENDPOINT=$(az cognitiveservices account show -n "$ACCOUNT" -g "$RG" \
  --query "properties.endpoint" -o tsv)
KEY=$(az cognitiveservices account keys list -n "$ACCOUNT" -g "$RG" \
  --query "key1" -o tsv)

echo
echo ">> Put these in your .env:"
echo "AZURE_OPENAI_ENDPOINT=$ENDPOINT"
echo "AZURE_OPENAI_API_KEY=$KEY"
echo "AZURE_OPENAI_DEPLOYMENT=$DEPLOYMENT"
echo
echo "Note: gpt-5-mini availability varies by region. If the deployment is"
echo "rejected, check the model catalog in the Foundry portal for the exact"
echo "model name/version available to you and set MODEL / MODEL_VERSION above."
