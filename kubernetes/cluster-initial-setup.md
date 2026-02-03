Md
# Kubernetes Cluster Health Check Runbook

## Document Overview
Audience: SRE / Platform / On-call Engineers  
Cluster Type: Production Kubernetes  
Frequency: Daily / Incident-based  
Last Updated: (fill manually)

---

## 1. Access & Context Validation

### Verify Kubernetes Context
```bash
kubectl config current-context
Expected:
Correct production cluster context
If Not Healthy:
Copy code
Bash
kubectl config use-context <context-name>
2. Kubernetes API Server Health
API Server Reachability
Copy code
Bash
kubectl get nodes
Healthy State:
API responds quickly
Nodes are listed
If Not Healthy:
Verify control-plane connectivity
Check API server logs
3. Node Health Checks
Node Status
Copy code
Bash
kubectl get nodes -o wide
Status
Meaning
Ready
Node healthy
NotReady
Node unhealthy
Node Diagnostics
Copy code
Bash
kubectl describe node <node-name>
Check For:
MemoryPressure
DiskPressure
PIDPressure
Network issues
4. Pod Health (All Namespaces)
Pod Status
Copy code
Bash
kubectl get pods -A
Unhealthy States:
CrashLoopBackOff
ImagePullBackOff
Pending
Pod Debugging
Copy code
Bash
kubectl describe pod <pod> -n <namespace>
kubectl logs <pod> -n <namespace>
5. Control Plane Health
kube-system Pods
Copy code
Bash
kubectl get pods -n kube-system
Critical Components:
kube-apiserver
kube-scheduler
kube-controller-manager
etcd
coredns
Healthy State:
All pods in Running state
6. etcd Health
etcd Logs
Copy code
Bash
kubectl logs -n kube-system etcd-<node-name>
Healthy Indicators:
Stable leader
No frequent elections
No timeout errors
7. DNS (CoreDNS) Health
CoreDNS Pods
Copy code
Bash
kubectl get pods -n kube-system -l k8s-app=kube-dns
DNS Resolution Test
Copy code
Bash
kubectl run dns-test --image=busybox --rm -it --restart=Never -- nslookup kubernetes.default
Expected:
DNS resolution succeeds
8. Resource Utilization
Node Resource Usage
Copy code
Bash
kubectl top nodes
Pod Resource Usage
Copy code
Bash
kubectl top pods -A
If Usage Is High:
Scale workloads
Investigate memory leaks
Add nodes if required
9. Storage Health
Persistent Volumes
Copy code
Bash
kubectl get pv
kubectl get pvc -A
Healthy State:
PV: Bound
PVC: Bound
If Not Healthy:
Check CSI driver logs
Validate storage backend (EBS, Ceph, NFS, etc.)
10. Network Health
CNI Plugin Status
Copy code
Bash
kubectl get pods -n kube-system | grep -E "calico|cilium|weave|flannel"
Healthy State:
All CNI pods running
11. Services & Ingress Health
Services
Copy code
Bash
kubectl get svc -A
Ingress
Copy code
Bash
kubectl get ingress -A
Endpoints
Copy code
Bash
kubectl get endpoints -A
Healthy State:
Services have endpoints attached
12. Cluster Events
Recent Events
Copy code
Bash
kubectl get events -A --sort-by=.metadata.creationTimestamp
Watch For:
FailedScheduling
ImagePullBackOff
Node pressure warnings
13. Security & Certificates
Certificate Signing Requests
Copy code
Bash
kubectl get csr
Action:
Approve pending CSRs if valid
Rotate certificates nearing expiry
14. Final Health Checklist
Check
Status
API Server
OK
Nodes
OK
Pods
OK
Control Plane
OK
DNS
OK
Storage
OK
Network
OK
No Critical Events
OK