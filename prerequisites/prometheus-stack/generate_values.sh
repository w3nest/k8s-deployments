#!/bin/bash

# Set dynamic variables, these could come from environment variables, CLI arguments, or any other source
export TOOLING_DOMAIN=$(kubectl get cm cluster-config -n apps -o jsonpath='{.data.toolingDomain}') 

# Process the template using envsubst
envsubst < values.yaml.tpl > values.yaml