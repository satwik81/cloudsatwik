#!/usr/bin/env bash
set -e

# ===== CONFIG =====
SOURCE_REPO_URL="https://gitlab.com/mygroup/monorepo.git"
DEST_BASE_URL="https://gitlab.com/mygroup/mysubgroup"
BRANCH="main"

FOLDERS=(
  service-a
  service-b
  infra
)

# ===== LOOP =====
for folder in "${FOLDERS[@]}"; do
  echo "=============================="
  echo "Processing folder: $folder"
  echo "=============================="

  # Step 1: clone the repo (folder name at the end)
  git clone "$DEST_BASE_URL/$folder.git"

  # Step 2: go to the cloned folder
  cd "$folder"

  # Step 3: copy from source repo
  cp -r "../monorepo/$folder/." .

  # Step 4: git add
  git add .

  # Step 5: git commit
  git commit -m "Initial import of $folder from monorepo"

  # Step 6: git push
  git push origin "$BRANCH"

  # Step 7: go back
  cd ..
done

echo "All folders processed successfully ✅"