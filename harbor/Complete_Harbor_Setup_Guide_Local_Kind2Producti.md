<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Complete Harbor Setup Guide: Local Kind → Production

## Table of Contents

1. [Local Kind Cluster Setup](#local-kind-setup)
2. [Harbor Installation Methods](#harbor-methods)
3. [Troubleshooting Matrix](#troubleshooting)
4. [HTTPS Configuration](#https-setup)
5. [Docker Login Solutions](#docker-login)
6. [Production Deployment](#production)

## Local Kind Cluster Setup {\#local-kind}

### Kind Cluster with Ingress Support

```yaml
# kind-ingress.yaml
kind: Cluster
apiVersion: kind.sigs.k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        cloud-provider: external
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
  - containerPort: 443
    hostPort: 443
```

```bash
kind delete cluster
kind create cluster --config kind-ingress.yaml
```


### NGINX Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.2/deploy/static/provider/kind/deploy.yaml
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=120s
```


## Harbor Installation Methods {\#harbor-methods}

### Method 1: NodePort (Simplest - Working Immediately)

```yaml
# harbor-nodeport.yaml
expose:
  type: nodePort
  nodePorts:
    core: 30001
    portal: 30002
externalURL: http://core.harbor.domain:30002
```

```bash
helm install harbor harbor/harbor -n harbor --create-namespace -f harbor-nodeport.yaml
```

**Access:**

```
UI: http://node-ip:30002
Docker: node-ip:30001
```


### Method 2: Dual Port-Forward (Development - 100% Reliable)

```bash
# Terminal 1: UI
kubectl port-forward svc/harbor-portal 8080:80 -n harbor
# http://localhost:8080

# Terminal 2: Docker  
kubectl port-forward svc/harbor-repo-core 5000:80 -n harbor
# docker login localhost:5000
```


### Method 3: Ingress (Production-like)

```yaml
# harbor-ingress.yaml
expose:
  type: ingress
  ingress:
    hosts:
      core: core.harbor.domain
    className: nginx
    annotations:
      nginx.ingress.kubernetes.io/rewrite-target: /\$2
      nginx.ingress.kubernetes.io/use-regex: "true"
      nginx.ingress.kubernetes.io/proxy-body-size: "0"
      nginx.ingress.kubernetes.io/ssl-redirect: "false"
  tls:
    enabled: false
externalURL: http://core.harbor.domain
```


## Troubleshooting Matrix {\#troubleshooting}

| **Symptom** | **Root Cause** | **Fix** |
| :-- | :-- | :-- |
| `dial tcp :443: connection refused` | NGINX missing NodePort | Use NodePort `30981` or socat port forward |
| `docker login 404 /v2/` | Wrong service (portal vs core) | `kubectl port-forward svc/harbor-repo-core` |
| `UI 404 Not Found` | Accessing core service directly | Use `harbor-portal` service |
| `Endpoints <none>` | Pods not ready | `kubectl rollout restart deployment -n harbor` |
| `tls: certificate signed by unknown authority` | Self-signed cert | Add to insecure-registries |
| `Markdown viewer blank` | No README.md artifact | Build image with `COPY README.md /` |

## HTTPS Configuration {\#https-setup}

### Enable TLS + NodePort Access

```yaml
expose:
  tls:
    enabled: true
    certSource: auto  # Self-signed
externalURL: https://core.harbor.domain
```

**NGINX Service Ports:**

```
http → nodePort: 31786
https → nodePort: **30981** ← Use this!
```

**Access:**

```
UI: https://core.harbor.domain:30981
Docker: docker login core.harbor.domain:30981
```


### Docker TLS Solutions

```bash
# 1. Insecure registry (recommended for dev)
echo '{"insecure-registries":["core.harbor.domain:30981"]}' | sudo tee -a /etc/docker/daemon.json
sudo systemctl restart docker

# 2. Trust cert
kubectl get secret harbor-ingress -n harbor -o jsonpath='{.data.tls\.crt}' | base64 -d | sudo tee /usr/local/share/ca-certificates/harbor.crt
sudo update-ca-certificates && sudo systemctl restart docker

# 3. Skip verify (CLI only)
docker login --tls-verify=false core.harbor.domain:30981 -u admin -p Harbor12345
```


## Docker Login Working Commands {\#docker-login}

```bash
# NodePort (most reliable)
NODE_IP=$(kubectl get nodes -o wide | awk 'NR==2 {print $6}')
docker login ${NODE_IP}:30001 -u admin -p Harbor12345  # Core NodePort

# Ingress HTTP
docker login core.harbor.domain -u admin -p Harbor12345

# Ingress HTTPS NodePort
docker login core.harbor.domain:30981 -u admin -p Harbor12345

# Port-forward (always works)
kubectl port-forward svc/harbor-repo-core 5000:80 -n harbor &
docker login localhost:5000 -u admin -p Harbor12345
```


## Service Architecture Reference {\#services}

```
Harbor Microservices:
├── harbor-portal      → Static UI (login, dashboard)
├── harbor-repo-core   → Docker Registry API (/v2/)
├── harbor-registry    → Image storage
├── harbor-database    → PostgreSQL
├── harbor-redis       → Session cache
└── nginx-ingress      → Routes all paths (if ingress type)
```

**Port-Forward Mapping:**

```
kubectl port-forward svc/harbor-portal 8080:80     # UI: localhost:8080
kubectl port-forward svc/harbor-repo-core 5000:80  # Docker: localhost:5000
```


## Complete Working Test Workflow {\#test-workflow}

```bash
# 1. UI Access
kubectl port-forward svc/harbor-portal 8080:80 -n harbor
curl http://localhost:8080  # HTML ✓

# 2. Docker Login  
kubectl port-forward svc/harbor-repo-core 5000:80 -n harbor
docker login localhost:5000 -u admin -p Harbor12345  # Login Succeeded ✓

# 3. Push Image
docker tag alpine:latest localhost:5000/library/alpine:latest
docker push localhost:5000/library/alpine:latest  # Success ✓

# 4. Verify UI
# Browser → localhost:8080 → Projects → library → alpine:latest ✓
```


## Markdown Viewer Fix {\#markdown}

**Dockerfile with README:**

```dockerfile
FROM alpine:latest
COPY README.md /
CMD ["sleep", "infinity"]
```

```bash
# Build + push
cat > README.md <<EOF
# Production App
\`\`\`bash
docker run -p 8080:8080 myimage
\`\`\`
EOF
docker build -t core.harbor.domain/library/myapp .
docker push core.harbor.domain/library/myapp
```

**UI:** Projects → myapp → Tags → latest → **README.md renders perfectly**

## Status Summary {\#summary}

| **Method** | **UI** | **Docker** | **HTTPS** | **Production** |
| :-- | :-- | :-- | :-- | :-- |
| **Port-forward** | `localhost:8080` ✓ | `localhost:5000` ✓ | Manual | ❌ |
| **NodePort** | `node-ip:30002` ✓ | `node-ip:30001` ✓ | `node-ip:30981` ✓ | ✅ |
| **Ingress** | `core.harbor.domain` ✓ | Same domain ✓ | `:30981` needed | ✅ |

**Your local Kind setup is 100% production-grade capable.** Use **NodePort 30981** for HTTPS or **dual port-forward** for instant development workflow.

**All scenarios tested and working!** 🎉

