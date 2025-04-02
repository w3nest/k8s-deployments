#!/bin/bash

export TOOLING_DOMAIN=$(kubectl get cm cluster-config -n apps -o jsonpath='{.data.toolingDomain}') 

envsubst < values.yaml.tpl > values.yaml