#!/usr/bin/env bash
# Deploy the vulnerable TARGET to Azure Container Apps.
# Edit the vars, then: bash deploy/deploy_target.sh
set -euo pipefail

RG="rg-pentest-workshop"
LOCATION="eastus"
ENV="cae-pentest-workshop"
APP="target-site"
# Your colleague's image once you have it; defaults to Juice Shop for testing.
IMAGE="${IMAGE:-bkimminich/juice-shop:latest}"
TARGET_PORT="${TARGET_PORT:-3000}"

echo ">> Resource group"
az group create -n "$RG" -l "$LOCATION" -o none

echo ">> Container Apps environment"
az containerapp env create -n "$ENV" -g "$RG" -l "$LOCATION" -o none

echo ">> Deploy target: $IMAGE"
az containerapp create \
  -n "$APP" -g "$RG" --environment "$ENV" \
  --image "$IMAGE" \
  --target-port "$TARGET_PORT" \
  --ingress external \
  --min-replicas 1 --max-replicas 1 \
  --cpu 0.5 --memory 1.0Gi \
  -o none

URL=$(az containerapp show -n "$APP" -g "$RG" \
  --query "properties.configuration.ingress.fqdn" -o tsv)
echo
echo ">> Target is live at: https://$URL"
echo ">> Set this in your .env:   TARGET_URL=https://$URL"
echo
echo "Clean up afterward with:   az group delete -n $RG --yes --no-wait"

# ---------------------------------------------------------------------------
# HARDENING (optional, defense-in-depth): put the environment in a VNet and
# deny outbound internet from the target's subnet with an NSG, so a popped
# target can't phone home. This is fiddlier; do it if you have time. The
# agent-side scope allowlist (scope.py) is the primary control regardless.
#
#   az network vnet create -g "$RG" -n vnet-lab --address-prefix 10.0.0.0/16 \
#     --subnet-name snet-apps --subnet-prefix 10.0.0.0/23
#   az network nsg create -g "$RG" -n nsg-lab
#   az network nsg rule create -g "$RG" --nsg-name nsg-lab -n deny-internet-out \
#     --priority 4096 --direction Outbound --access Deny \
#     --destination-address-prefixes Internet --protocol '*' \
#     --source-port-ranges '*' --destination-port-ranges '*'
#   # ...associate the NSG to snet-apps and create the env with
#   #    --infrastructure-subnet-resource-id <snet-apps id> --internal-only true
# ---------------------------------------------------------------------------
