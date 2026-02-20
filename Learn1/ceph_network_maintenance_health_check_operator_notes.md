# Ceph Network Maintenance & Health Check – Operator Notes

This document is a **practical operator cheat‑sheet** for checking Ceph cluster health and safely handling **network / switch OS upgrades**.

---

## 1. Overall Cluster Health (Always Start Here)

```bash
ceph -s
```

Healthy:
- HEALTH_OK
- or HEALTH_WARN (read details)

Stop if:
- HEALTH_ERR
- MON quorum lost

---

## 2. Monitor (MON) Health – Cluster Brain

```bash
ceph mon stat
```

```bash
ceph quorum_status
```

Check:
- All MONs present
- Quorum formed

---

## 3. OSD Status – Most Important During Network Work

### Summary
```bash
ceph osd stat
```

### Detailed topology
```bash
ceph osd tree
```

All OSDs should be:
- up
- in

---

## 4. Placement Groups (PGs)

```bash
ceph pg stat
```

Healthy state:
```
active+clean
```

Warning states:
- peering
- degraded
- undersized
- stale

---

## 5. CephFS Health (If Using CephFS / RWX PVCs)

```bash
ceph fs status
```

```bash
ceph mds stat
```

Healthy example:
```
myfs: 1/1 active, 1 standby
```

---

## 6. Performance Quick Checks

```bash
ceph osd perf
```

Rule of thumb:
- <10 ms → good
- >50 ms → investigate

---

## 7. Crash & Error Inspection

```bash
ceph crash ls
```

```bash
ceph health detail
```

---

## 8. BEFORE Network / Switch OS Upgrade (CRITICAL)

### Set maintenance protection

```bash
ceph osd set noout
```

Meaning:
- OSDs may go down temporarily
- Ceph will NOT mark them out
- No rebalancing / recovery storms

### Confirm flag

```bash
ceph osd dump | grep noout
```

You should see:
```
flags noout
```

---

## 9. DURING Network Upgrade

Keep monitoring:

```bash
ceph -s
```

Watch for:
- MON quorum
- OSD flapping
- HEALTH_ERR

---

## 10. AFTER Network Is Stable

### Remove maintenance protection

```bash
ceph osd unset noout
```

Why this matters:
- Allows normal recovery
- Protects data in real failures

⚠️ Do NOT forget this step

---

## 11. Optional (Advanced Maintenance Flags)

| Flag | Purpose |
|-----|--------|
| noout | Prevent OSDs being marked out |
| norebalance | Stop rebalancing |
| nobackfill | Stop backfill |
| pause | Freeze all IO (rare) |

Example:
```bash
ceph osd set norebalance
```

---

## 12. One‑Command Health Check

```bash
ceph -s && ceph osd stat && ceph pg stat && ceph fs status
```

If this looks clean → cluster is safe.

---

## 13. Golden Operator Rules

- Clean outage > flapping network
- Always set noout before maintenance
- Always unset noout after maintenance
- Monitor MON quorum continuously
- Expect recovery AFTER network comes back

---

## 14. When to Stop the Upgrade Immediately

Stop if you see:
- MON quorum lost
- Many OSDs flapping
- PGs stuck in peering
- CephFS MDS stuck in replay

---

## 15. One‑Line Explanation for Teams

"We set `noout` so Ceph doesn’t rebalance during temporary network loss, and unset it once the network is stable."

---

End of document.

