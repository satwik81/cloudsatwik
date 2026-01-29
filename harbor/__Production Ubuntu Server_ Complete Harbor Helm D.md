<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## **Production Ubuntu Server: Complete Harbor Helm Deployment**

Here's the **exact production-ready setup** for Ubuntu server with Kubernetes + Harbor via Helm.

## **1. Prerequisites (Ubuntu Server)**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Install containerd (alternative runtime)
sudo apt install -y containerd

# Install Kubernetes components
curl -s https://packages.cloud.google.com/apt/doc/install-linux-mint.sh | sudo bash
sudo apt install -y kubelet kubeadm kubectl

# Disable swap
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
```


## **2. Initialize Production K8s Cluster**

```bash
# Reset (if needed)
sudo kubeadm reset -f

# Initialize control-plane
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --control-plane-endpoint=$(hostname -I | awk '{print $1}')

# Setup kubeconfig
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Taint control-plane (allow workloads)
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```


## **3. Install CNI (Calico/Flannel)**

```bash
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml
```


## **4. Install NGINX Ingress Controller (Production)**

```bash
# Add repo
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.2/deploy/static/provider/cloud/deploy.yaml
```


## **5. Install Cert-Manager (Production TLS)**

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```


## **6. Production Harbor Values (`production-values.yaml`)**

```yaml
# External access
externalURL: https://harbor.yourdomain.com

expose:
  type: ingress
  ingress:
    hosts:
      core: harbor.yourdomain.com
      notary: notary.yourdomain.com
    className: nginx
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt-prod
      nginx.ingress.kubernetes.io/proxy-body-size: "0"
      nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
      nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
  tls:
    enabled: true
    certSource: secret
    secret:
      secretName: harbor-tls
      domainNames:
        - harbor.yourdomain.com
        - notary.yourdomain.com

# Production storage (use Longhorn/Rook)
persistence:
  enabled: true
  persistentVolumeClaim:
    registry:
      storageClass: "longhorn"  # or your storage class
      size: 50Gi
    chartmuseum:
      storageClass: "longhorn"
      size: 5Gi
    database:
      storageClass: "longhorn"
      size: 5Gi
    redis:
      storageClass: "longhorn"
      size: 1Gi
    jobservice:
      storageClass: "longhorn"
      size: 1Gi

# Production database (external PostgreSQL recommended)
database:
  type: external  # Use RDS/Aurora
  external:
    host: your-rds-endpoint
    port: 5432
    database: harbor
    username: harbor
    password: "your-secure-password"

# Security
harborAdminPassword: "SuperSecurePassword123!"

# Resource limits
resources:
  limits:
    cpu: 2000m
    memory: 4Gi
  requests:
    cpu: 1000m
    memory: 2Gi

# Enable vulnerability scanning
trivy:
  enabled: true
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
```


## **7. Production ClusterIssuer (Let's Encrypt)**

```yaml
# letsencrypt-prod.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@domain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: harbor-tls
  namespace: harbor
spec:
  secretName: harbor-tls
  dnsNames:
  - harbor.yourdomain.com
  - notary.yourdomain.com
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
```

```bash
kubectl apply -f letsencrypt-prod.yaml
```


## **8. Deploy Production Harbor**

```bash
# Add Harbor repo
helm repo add harbor https://helm.goharbor.io
helm repo update

# Install
helm install harbor harbor/harbor \
  --namespace harbor --create-namespace \
  -f production-values.yaml --timeout 20m --wait
```


## **9. Verify Production Deployment**

```bash
# All pods healthy
kubectl get pods -n harbor -w

# Ingress ready
kubectl get ingress -n harbor

# Certificate issued
kubectl get certificate -n harbor

# Services LoadBalancer IPs
kubectl get svc -n ingress-nginx
```


## **10. Production Access**

```
🌐 UI: https://harbor.yourdomain.com (Let's Encrypt cert)
🐳 Docker: docker login harbor.yourdomain.com -u admin -p SuperSecurePassword123!
📦 Push: docker push harbor.yourdomain.com/project/image:tag
```


## **11. Production Hardening**

```bash
# RBAC - Restrict access
kubectl create rolebinding harbor-admin \
  --clusterrole=cluster-admin \
  --user=admin \
  --namespace=harbor

# NetworkPolicy
kubectl apply -f https://raw.githubusercontent.com/goharbor/harbor-helm/main/examples/network-policy.yaml

# Monitoring (Prometheus)
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
```


## **12. Scale Workers (Production)**

```bash
# Join worker nodes
sudo kubeadm join your-control-plane-ip:6443 --token abcdef.1234567890abcdef \
  --discovery-token-ca-cert-hash sha256:your-hash

# Scale deployments
kubectl scale deployment harbor-core -n harbor --replicas=3
```


## **Production Checklist**

```
☐ Ubuntu 20.04/22.04 LTS
☐ Kubernetes 1.28+ (kubeadm)
☐ NGINX Ingress Controller (LoadBalancer)
☐ Cert-Manager + Let's Encrypt
☐ Persistent Storage (Longhorn/Rook-Ceph)
☐ External PostgreSQL/Redis
☐ Resource limits/requests
☐ NetworkPolicies
☐ Monitoring (Prometheus/Grafana)
☐ Backup strategy
☐ Multi-zone HA (3+ masters)
```

**This setup gives you:**

- ✅ **Production-grade** HTTPS Harbor
- ✅ **Let's Encrypt** auto TLS certs
- ✅ **LoadBalancer** external access
- ✅ **Persistent storage**
- ✅ **Vulnerability scanning**
- ✅ **RBAC security**
- ✅ **Horizontal scaling**

**Replace `harbor.yourdomain.com` + storage/database endpoints → Deploy → Production ready! 🚀**
<span style="display:none">[^1][^10][^2][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://support.tools/setting-up-harbor-registry-kubernetes-helm/

[^2]: https://goharbor.io/docs/1.10/working-with-projects/working-with-images/managing-helm-charts/

[^3]: https://k8s.co.il/kubernetes/deploying-harbor-kind-and-helm-charts/

[^4]: https://github.com/goharbor/harbor-operator/blob/main/docs/installation/by-helm-chart.md

[^5]: https://www.cncf.io/blog/2026/01/05/deploying-harbor-on-kubernetes-using-helm/

[^6]: https://github.com/macneib/harbor-helm-chart

[^7]: https://github.com/goharbor/harbor-helm

[^8]: https://goharbor.io/docs/1.10/install-config/harbor-ha-helm/

[^9]: https://ruzickap.github.io/k8s-harbor/part-04/

[^10]: https://ruzickap.github.io/k8s-harbor/part-06/

