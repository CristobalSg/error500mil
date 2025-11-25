#!/usr/bin/env bash

admin_password="$(head -c 512 /dev/urandom | LC_CTYPE=C tr -cd 'a-zA-Z0-9!-/' | head -c 32)Aa2*"

cat <<EOF > admin-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: admin-secret
  namespace: sgh
type: kubernetes.io/basic-auth
stringData:
  username: admin
  password: $admin_password
EOF

postgres_password=$(head -c 512 /dev/urandom | LC_CTYPE=C tr -cd 'a-zA-Z0-9' | head -c 32)

cat <<EOF > postgres-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: sgh
type: kubernetes.io/basic-auth
stringData:
  username: sgh_admin
  password: $postgres_password
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-url-secret
  namespace: sgh
stringData:
  url: postgresql://sgh_admin:$postgres_password@postgres-cluster-rw.sgh.svc/sgh_production
EOF

jwt_secret=$(head -c 512 /dev/urandom | LC_CTYPE=C tr -cd 'a-zA-Z0-9' | head -c 64)
refresh_secret=$(head -c 512 /dev/urandom | LC_CTYPE=C tr -cd 'a-zA-Z0-9' | head -c 64)

cat <<EOF > jwt-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: jwt-secret
  namespace: sgh
stringData:
  secret: $jwt_secret
  refresh: $refresh_secret
EOF

