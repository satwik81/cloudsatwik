
MY APPROACH OF SLM DEPLOYMENT & USAGE IN K8S CLUSTER

PREREQUISITES 
GPU

list the model and download the model from hugging face to local system 

  create an account login to hugging face, we can get one token from our profile

  In our system terminal we have to install hugging face cli package

with the cli installed, login by giving the token cmd source: hf auth

it prompts for credentials store click NO

after cli installation. go to hugging face copy the model download command though the hugging face cli command 


after downloading the model, we have a bunch of model files in our system. better if we have all under one single folder.

COPY the model files into ubuntu server.

post that,

Initially create a cephFs storage class and volume claim to retain the model files.

create a busybox pod and mount the volumeclaim to this that helps to store the model files even if pod crashes.

creata deployment of vllm which we can use to run the model and use it.

curl the request to vllm via api with the path and giving a query so that we can get a response from the model.

Next steps will be the openwebui to interact with the model with the UI.

### Deployment 

apiVersion: apps/v1
kind: Deployment
metadata:
  name: open-webui
  namespace: open-webui
spec:
  replicas: 1
  selector:
    matchLabels:
      app: open-webui
  template:
    metadata:
      labels:
        app: open-webui
    spec:
      containers:
        - name: open-webui
          image: ghcr.io/open-webui/open-webui:main
          ports:
            - containerPort: 8080
          env:
            - name: OPENAI_API_BASE_URL
              value: "http://<service-name>.<namespace>.svc.cluster.local:<port>/v1"
            - name: OPENAI_API_KEY
              value: "dummy"          # Required field, but can be fake if your model doesn't auth
            - name: WEBUI_AUTH
              value: "false"          # Set to true for production
          volumeMounts:
            - name: webui-data
              mountPath: /app/backend/data
      volumes:
        - name: webui-data
          persistentVolumeClaim:
             claimName: open-webui-pvc              # Replace with PVC for persistence
---
apiVersion: v1
kind: Service
metadata:
  name: open-webui
  namespace: open-webui
spec:
  selector:
    app: open-webui
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP                    # Change to LoadBalancer or use Ingress for external access
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: open-webui-pvc
  namespace: open-webui
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  # storageClassName: standard   # Uncomment and set if your cluster needs a specific StorageClass
