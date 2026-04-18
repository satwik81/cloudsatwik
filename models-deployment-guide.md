
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
