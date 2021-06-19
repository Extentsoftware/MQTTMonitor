# Signing in 
## To sign in

```
az account set --subscription 73a97781-98ea-4939-aa9d-f4c6233b011e
az aks get-credentials --resource-group Bongo --name Bongo
```

## List deployments
```
kubectl get deployments --namespace dev
```

## Deploy single pod with all containers
```
cd chart
helm install mqttmonitor mqttmonitor --namespace dev
```

## Deploy as separate pods
```
kubectl apply -f mqttbongo.yml
```


# get the pods IP
kubectl get svc --namespace dev mqttmonitor --template "{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}"

# Create a cluster on Azure

```
kubectl create namespace -name dev
```

# Add the official stable repository
```
helm repo add stable https://kubernetes-charts.storage.googleapis.com/
```

# Use Helm to deploy an NGINX ingress controller

Refer to:
https://docs.microsoft.com/en-gb/azure/aks/ingress-basic

```
helm install nginx-ingress stable/nginx-ingress --namespace dev --set controller.replicaCount=2 --set controller.nodeSelector."beta\.kubernetes\.io/os"=linux --set defaultBackend.nodeSelector."beta\.kubernetes\.io/os"=linux
```

# Create public IP
Create public IP in resource group MC_Bongo_Bongo_uksouth (resource group of cluster nodes)

https://docs.microsoft.com/en-us/azure/aks/static-ip 
```
az network public-ip create --resource-group MC_Bongo_Bongo_uksouth --name BongoPublicIP --sku Standard --allocation-method static
```

change IP address in mosquitto Service to the Public IP address

# Useful Commands
cd charts
kubectl apply -f mqttbongo.yaml

kubectl get --namespace dev svc 

kubectl delete -f mqttbongo.yaml

==> 51.132.212.244
az network public-ip show --resource-group Farm --name FarmPublicIP --query ipAddress --output tsv

az aks show --resource-group Farm --name FarmCluster --query addonProfiles.httpApplicationRouting.config.HTTPApplicationRoutingZoneName -o table

bongo.uksouth.cloudapp.azure.com