# Create a cluster on Azure

`kubectl create namespace -name dev`

# Create a namespace for your ingress resources
//`kubectl create namespace ingress-basic`

# Add the official stable repository
`helm repo add stable https://kubernetes-charts.storage.googleapis.com/`

# Use Helm to deploy an NGINX ingress controller

Refer to:
https://docs.microsoft.com/en-gb/azure/aks/ingress-basic

```
helm install nginx-ingress stable/nginx-ingress --namespace dev --set controller.replicaCount=2 --set controller.nodeSelector."beta\.kubernetes\.io/os"=linux --set defaultBackend.nodeSelector."beta\.kubernetes\.io/os"=linux
```

kubectl apply -f mqttbongo.yaml  



// ----------------------------------------
//helm uninstall mqttmonitor --namespace farm
// ## Install mqttmonitor
//helm install mqttmonitor -name MQTTMonitor --namespace dev

## Browse kubectl 
az aks browse --resource-group farm --name farmcluster

## 

kubectl get --namespace dev svc 

kubectl delete -f mqttbongo.yaml

https://docs.microsoft.com/en-us/azure/aks/static-ip 
az network public-ip create --resource-group Farm --name FarmPublicIP --sku Basic --allocation-method static
==> 51.132.212.244
az network public-ip show --resource-group Farm --name FarmPublicIP --query ipAddress --output tsv

az aks show --resource-group Farm --name FarmCluster --query addonProfiles.httpApplicationRouting.config.HTTPApplicationRoutingZoneName -o table

bongo.uksouth.cloudapp.azure.com