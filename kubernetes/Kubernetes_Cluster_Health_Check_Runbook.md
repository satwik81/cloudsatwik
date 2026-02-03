
# Kubernetes Cluster Health Check Runbook

## Purpose
This runbook provides standard health checks for a Kubernetes production cluster.
It is intended for on-call engineers, SREs, and platform teams to quickly assess
cluster health and take corrective action.

---

## When to Use
- Daily cluster validation
- Incident response
- Post-deployment verification
- Before maintenance or scaling

---

## Cluster Overview Health

| Check | Command | Healthy State | Action if Unhealthy |
|------|--------|---------------|---------------------|
| Cluster API | `kubectl cluster-info` | API reachable | Check control-plane & API logs |
| API Health | `kubectl get --raw=/healthz` | ok | Restart kube-apiserver |
| Readiness | `kubectl get --raw=/readyz` | ok | Inspect failing component |
| Liveness | `kubectl get --raw=/livez` | ok | Check control-plane stability |

---

## Node Health Checks

| Check | Command | Healthy State | Action if Unhealthy |
|------|--------|---------------|---------------------|
| Node Status | `kubectl get nodes` | All nodes Ready | Inspect node & kubelet |
| Node Conditions | `kubectl describe node <node>` | No pressure conditions | Free disk/memory or cordon node |
| Node Resources | `kubectl top nodes` | CPU & memory < 80% | Scale nodes/workloads |

---

## Pod & Workload Health

| Check | Command | Healthy State | Action if Unhealthy |
|------|--------|---------------|---------------------|
| All Pods | `kubectl get pods -A` | Running / Completed | Investigate failing pods |
| Failed Pods | `kubectl get pods -A | grep -v Running` | No output | Check logs & events |
| Deployments | `kubectl get deploy -A` | Ready = Desired | Check rollout status |
| StatefulSets | `kubectl get sts -A` | All replicas ready | Check pod ordering & PVCs |
| DaemonSets | `kubectl get ds -A` | Desired = Ready | Check node selectors |

---

## Control Plane & etcd

| Check | Command | Healthy State | Action if Unhealthy |
|------|--------|---------------|---------------------|
| kube-system Pods | `kubectl get pods -n kube-system` | All Running | Restart failed component |
| etcd Health | `etcdctl endpoint health` | Healthy | Immediate escalation |
| etcd Latency | `etcdctl endpoint status` | Low latency | Check disk & network |

---

## Networking & DNS

| Check | Command | Healthy State | Action if Unhealthy |
|------|--------|---------------|---------------------|
| CoreDNS Pods | `kubectl get pods -n kube-system -l k8s-app=kube-dns` | Running | Check CoreDNS logs |
| DNS Resolution | `nslookup kubernetes.default` | Resolves | Check CoreDNS / CNI |
| CNI Plugins | `kubectl get pods -n kube-system | grep cni` | Running | Restart CNI |

---

## Storage Health

| Check | Command | Healthy State | Action if Unhealthy |
|------|--------|---------------|---------------------|
| Persistent Volumes | `kubectl get pv` | Available / Bound | Check storage backend |
| Persistent Claims | `kubectl get pvc -A` | Bound | Fix storage class |
| CSI Drivers | `kubectl get pods -n kube-system | grep csi` | Running | Restart CSI |

---

## Events & Error Detection

| Check | Command | Healthy State | Action if Unhealthy |
|------|--------|---------------|---------------------|
| Cluster Events | `kubectl get events -A --sort-by=.metadata.creationTimestamp` | No repeating errors | Resolve root cause |
| OOM Kills | `kubectl get events -A | grep OOM` | None | Increase memory limits |
| Scheduling | `kubectl get events -A | grep FailedScheduling` | None | Add capacity |

---

## 30-Second On-Call Health Check

| Check | Command | Expected Result |
|------|--------|-----------------|
| Nodes | `kubectl get nodes` | All Ready |
| Pods | `kubectl get pods -A` | No failures |
| Events | `kubectl get events -A | tail` | No errors |
| Resources | `kubectl top nodes` | Below 80% |

---

## Best Practices
- Check nodes first, then pods, then workloads
- Events explain most failures
- Disk pressure is more dangerous than CPU pressure
- etcd latency often predicts outages
