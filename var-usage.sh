#!/bin/bash

# Check /var/log partition volume utilization

PARTITION="/var/log"
THRESHOLD=80  # Warning threshold percentage

# Get disk usage info
USAGE=$(df "$PARTITION" 2>/dev/null | awk 'NR==2 {print $5}' | tr -d '%')
TOTAL=$(df -h "$PARTITION" 2>/dev/null | awk 'NR==2 {print $2}')
USED=$(df -h "$PARTITION" 2>/dev/null | awk 'NR==2 {print $3}')
AVAIL=$(df -h "$PARTITION" 2>/dev/null | awk 'NR==2 {print $4}')
MOUNT=$(df "$PARTITION" 2>/dev/null | awk 'NR==2 {print $6}')

if [[ -z "$USAGE" ]]; then
  echo "ERROR: Could not retrieve usage for $PARTITION"
  exit 1
fi

# Display results
echo "============================================"
echo "  /var/log Partition Utilization Report"
echo "============================================"
echo "  Mount Point : $MOUNT"
echo "  Total Size  : $TOTAL"
echo "  Used        : $USED"
echo "  Available   : $AVAIL"
echo "  Utilization : $USAGE%"
echo "============================================"

# Status check
if [[ "$USAGE" -ge 90 ]]; then
  echo "  Status      : CRITICAL (>= 90%)"
  exit 2
elif [[ "$USAGE" -ge "$THRESHOLD" ]]; then
  echo "  Status      : WARNING (>= ${THRESHOLD}%)"
  exit 1
else
  echo "  Status      : OK"
  exit 0
fi