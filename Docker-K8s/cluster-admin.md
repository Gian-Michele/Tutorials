### POD with Cluster  admin privilege
A pod with cluster admin privilege could have the role to decide when scale up/down the other pods. The pods with cluster-admin privilege (configured with a specific service account) can work as a cluster control

Prometheus endpoins could be a pod to monitor to know the status of the system


Additionally is needed the token to connect to k8s with the role of cluster-admin. In order to do that the following action is needed:

# Option 1 to get the token for API Server usage

- the command to generate the service-account and the token associated is:

        kubectl -n kube-system apply -f admin-user.yaml

- the token can be recovered using the following commands:

	SERVICE_ACCOUNT=admin-user

	SECRET=$(kubectl -n kube-system get serviceaccount ${SERVICE_ACCOUNT} -o json | jq -Mr '.secrets[].name | select(contains("token"))')

	TOKEN=$(kubectl -n kube-system get secret ${SECRET} -o json | jq -Mr '.data.token' | base64 -d)

	echo($TOKEN)

- the printed token could be inserted in a secret as follow:
```yaml
apiVersion: v1
stringData:
  token.txt: |
     eyJhbGciOiJSUzI1....-V9CIeT1n82xi0M0sPgc_Jf6HKKzAhw
kind: Secret
metadata:
  name: my-token-secret
type: Opaque
```


- now apply the secret using the command

	kubectl -n nrtric apply -f my-token-secret.yml

- now the secret could be loaded in a pod deployment as a volume as in the deployment example below:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deploy-name
  labels:
    app: pod-test
spec:
  selector:
    matchLabels:
       app: my-app           
  replicas: 1
  template:
    metadata:
      labels:
        app: my-app
    spec:
      serviceAccountName: admin-user-nrtric
      containers:
       - name: pod-test
         image: pod-image:2.0.1
         # Always or IfNotPresent
         imagePullPolicy: Always
         volumeMounts:
         - name: pod-secret
           mountPath: /tmp

      volumes:
       - name: pod-secret
         secret:
           secretName: my-token-secret
```


# Option 2 to get token to API Server usage:

As described in [https://kubernetes.io/docs/concepts/security/service-accounts/](https://kubernetes.io/docs/concepts/security/service-accounts/) the token as to be assigned using a service account directly in the deployment. The command to generate a service-account is:

	kubectl apply -f admin-user.yaml

where admin-user.yaml contains the description of the service account:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kube-system
---
apiVersion: v1
kind: Secret
type: kubernetes.io/service-account-token
metadata:
  name: admin-user-sa-token
  namespace: kube-system
  annotations:
    kubernetes.io/service-account.name: admin-user
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kube-system
```

is used to create a service-account name admin-user that can be assigned at a pod looking the link: [https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/)

Following this new option is k8s that provide the token in the file **/var/run/secrets/kubernetes.io/serviceaccount/token** with the permission defined in the service account

the deployment needs of the service-account name and no more a secret needs to be passed as a volume. Look below the new deployment:


```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deploy-name
  labels:
    app: pod-test
spec:
  selector:
    matchLabels:
       app: my-app           
  replicas: 1
  template:
    metadata:
      labels:
        app: my-app
    spec:
      serviceAccountName: admin-user
      containers:
       - name: pod-test
         image: pod-image:2.0.1
         # Always or IfNotPresent
         imagePullPolicy: Always

```
