# 🔥 Ceph CRD Cleanup Guide

> This guide helps completely remove Rook-Ceph and its Kubernetes Custom Resource Definitions (CRDs), including stuck finalizers.

Maintainer: [Your Name]  
Source: Adapted from practical Ceph/Rook Kubernetes management experience.

---

## 🌟 Objective

Completely remove all **Rook-Ceph Custom Resource Definitions (CRDs)** and any remaining Ceph resources from the Kubernetes cluster, including stuck finalizers that block deletion.

---

## 🔍 Problem

When trying to delete Ceph CRDs, you may see delays or hangs. This happens because:

- Ceph Custom Resources (CRs) like `CephCluster`, `CephBlockPool`, etc., still exist.
- These CRs have `finalizers` that prevent Kubernetes from deleting them.
- The `rook-ceph-operator` is likely no longer running, so the finalizers never complete.

---

## ✅ Step-by-Step Cleanup

### 🔹 Step 1: List Remaining Ceph CRs

```bash
kubectl get cephclusters.ceph.rook.io -A
kubectl get cephblockpools.ceph.rook.io -A
kubectl get cephobjectstores.ceph.rook.io -A
kubectl get cephfilesystems.ceph.rook.io -A
kubectl get cephfilesystemsubvolumegroups.ceph.rook.io -A
```

---

### 🔹 Step 2: Remove Finalizers from Ceph CRs

```bash
for crd in cephclusters cephblockpools cephobjectstores cephfilesystems cephfilesystemsubvolumegroups; do
  for ns in $(kubectl get ns -o jsonpath="{.items[*].metadata.name}"); do
    for name in $(kubectl get ${crd}.ceph.rook.io -n $ns --no-headers --ignore-not-found | awk '{print $1}'); do
      echo "Removing finalizers from $crd $name in $ns"
      kubectl patch ${crd}.ceph.rook.io $name -n $ns -p '{"metadata":{"finalizers":[]}}' --type=merge
    done
  done
done
```

---

### 🔹 Step 3: Delete the Ceph CRDs (Forcefully)

```bash
for crd in $(kubectl get crd | grep -i ceph | awk '{print $1}'); do
  echo "Deleting CRD: $crd"
  kubectl delete crd "$crd" --grace-period=0 --force
done
```

---

### 🔹 Step 4: Confirm Cleanup

```bash
kubectl get crd | grep ceph
```

If no output, the cleanup is complete.

---

## ✅ Done!

You have successfully:

- Removed stuck Ceph CRs
- Deleted all Ceph CRDs
- Fully uninstalled the Ceph API from your cluster
