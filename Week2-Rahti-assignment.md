# Week 2: Containerization and OpenShift Deployment (CSC Rahti)

## Overview

In this week's assignment, we moved away from plain Virtual Machines (VMs) and containerized a web application using Docker and deployed it onto **CSC Rahti**, an OpenShift (Kubernetes) cloud platform.

The primary goal was to experience core cloud-native features: non-root container security, automated image building, edge TLS routing, scaling, and self-healing.

## Architecture

### High-Level Architecture Diagram

```text
+-----------------------------------------------------------------------------------+
|                            Local Machine (MacBook Pro M1)                         |
|                                                                                   |
|   cloud-services-2026/                                                            |
|    └── Week 2/                                                                    |
|         ├── index.html   (Web application source)                                |
|         └── Dockerfile   (Instructions for non-priv Nginx image)                  |
+------------------------------------------+----------------------------------------+
                                           |
                                           | git push origin main
                                           v
+-----------------------------------------------------------------------------------+
|                    GitHub Repository (cloud-services-2026)                       |
|   Stores source code in the "Week 2" sub-directory                               |
+------------------------------------------+----------------------------------------+
                                           |
                                           | oc new-app ... --context-dir="Week 2"
                                           v
+-----------------------------------------------------------------------------------+
|                        CSC Rahti Platform (OpenShift)                             |
|                                                                                   |
|   1. Build Pipeline: Fetches source -> Builds Docker Image                        |
|   2. Deployment: Runs 3 Container Replicas (Pods)                                 |
|   3. Service: Internal network balancer (Port 8080)                               |
|   4. Edge Route: Exposes public HTTPS endpoint (*.2.rahtiapp.fi)                  |
+-----------------------------------------------------------------------------------+

```

### Comparison:Week 1 (VPS Deployment) VS Week 2 (Containerized Deployment)

```text
+-----------------------------------------------------------------------------------+
|                        Week 1 (VM 虚拟机) vs Week 2 (云原生容器)                  |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ Week 1: VM 虚拟机模式 ]                                                        |
|  +-----------------------------------------------------------------------------+  |
|  | 硬件 -> 宿主机 OS -> 虚拟机管理软件 -> 完整客体 OS (很重) -> Web 软件           |  |
|  +-----------------------------------------------------------------------------+  |
|  缺点: 启动慢 (几分钟)、占用资源大、难以秒级扩容和自动修复。
|  比喻：盖了VM大别墅，只卖汉堡，如果之后向扩展生意，要一个一个盖大别墅，非常浪费钱和时间
|                                                                                   |
|  -------------------------------------------------------------------------------  |
|                                                                                   |
|  [ Week 2: Docker + Rahti 容器模式 ]                                             |
|  +-----------------------------------------------------------------------------+  |
|  | 你的电脑 (M1 Mac) -> GitHub (设计图) -> Rahti 大队长 (自动组装轻量餐车)     |  |
|  +-----------------------------------------------------------------------------+  |
|                                         |                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  | 运行在云端的 3 个轻量 Pod (秒级启动 / 损坏 4 秒内自动重建 / 公网 HTTPS 访问)   |  |
|  +-----------------------------------------------------------------------------+  |
|  比喻：把汉堡店做成了标准的餐车(Docker container) 并且只放了做汉堡必须的食材(HTML)和煎锅(nginx)                                                                             |
+-----------------------------------------------------------------------------------+

```

### Technical Concept Breakdown

- **Dockerfile:** Think of this as a "standard operating recipe". It tells the cloud platform which pre-configured base image to use and where to place the web application.
- **Non-root container security (port 8080):** OpenShift enforces strict security policies. Standard web servers try to bind to port 80, which requires administrator (root) access. Rahti removes root privileges to reduce the risk of container breakout. Moving the application to port 8080 allows the application to run without administrator privileges.
- **Pods:** A Pod is a running unit that contains the web container.
- **Scaling (`oc scale`):** Scaling to three replicas creates three identical application instances to handle more traffic.
- **Self-healing (`oc delete pod`):** If a Pod is deleted, OpenShift notices that the desired number of replicas is no longer running and automatically creates a replacement.

## Step-by-Step Implementation

### 1. Local File and Dockerfile Setup

Created a dedicated subdirectory named `Week 2` inside the `cloud-services-2026` repository.

#### `Week 2/index.html`

```html
<!doctype html>
<html>
  <head>
    <title>Week 2 Assignment</title>
  </head>
  <body>
    <h1>Week 2 Assignment</h1>
  </body>
</html>
```

#### `Week 2/Dockerfile`

```dockerfile
FROM nginxinc/nginx-unprivileged:alpine
COPY index.html /usr/share/nginx/html/
```

> **Note:** `nginxinc/nginx-unprivileged:alpine` naturally listens on port 8080 and runs as a non-privileged user by default.

### 2. Version Control and Git Cleanup

Configured `.gitignore` to prevent OS-generated `.DS_Store` files from polluting the repository, removed cached tracking files from Week 1, and pushed the new subdirectory to GitHub.

```bash
# Navigate to the repository root
cd ~/path/to/cloud-services-2026

# Remove tracked .DS_Store files from the Git index without deleting local files
git rm -r --cached .DS_Store 2>/dev/null
git rm -r --cached "Week 2/.DS_Store" 2>/dev/null

# Add a rule to ignore .DS_Store in this repository
echo ".DS_Store" >> .gitignore

# Stage, commit, and push
git add .
git commit -m "Add Week 2 setup, clean up .DS_Store and update gitignore"
git push origin main
```

### 3. Local Environment Setup (macOS M1)

Installed Homebrew (macOS Package Manager) and the OpenShift CLI (oc) tool on Apple Silicon:

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install OpenShift CLI
brew install openshift-cli

# Verify installation
oc version
```

### 4. Authentication and Project Selection

Authenticated into CSC Rahti using the web console token and verified project context:

```bash
# Log in using web-generated token
oc login https://api.2.rahti.csc.fi:6443 --token=<TOKEN>

# Set active project
oc project week2-assignment
```

### 5. Build, Deploy, and Route Configuration

Triggered an automated build pointing directly to the Week 2 subdirectory using --context-dir, then created an Edge TLS route:

```bash
# Build and deploy application from sub-directory
oc new-app https://github.com/Jess-Xu123/cloud-services-2026.git --context-dir="Week 2"

# Monitor build logs
oc logs -f bc/cloud-services-2026

# Create Edge TLS Route with automatic HTTP -> HTTPS redirect

oc create route edge cloud-services-2026 --service=cloud-services-2026 --insecure-policy=Redirect

# Inspect route details
oc get route
```

#### Route output

```text
NAME HOST/PORT SERVICES PORT TERMINATION WILDCARD
cloud-services-2026 cloud-services-2026-week2-assignment.2.rahtiapp.fi cloud-services-2026 8080-tcp edge/Redirect None
```

**Public domain:** <https://cloud-services-2026-week2-assignment.2.rahtiapp.fi>

### 6. Scaling and Self-Healing Test

Demonstrated Kubernetes orchestration resilience by scaling instances and deleting an active Pod:

#### Scale replicas to three

```bash
oc scale deployment/cloud-services-2026 --replicas=3
```

#### Verify Pod status

```bash
oc get pods
```

The output showed one completed build Pod (`cloud-services-2026-1-build`) and three active application Pods.

#### Delete an active Pod (simulate node outage)

```bash
oc delete pod cloud-services-2026-77cd8d747c-sk8t4
```

#### Verify immediate self-healing

```bash
oc get pods
```

The deleted Pod entered the `Terminating` state, and OpenShift automatically provisioned a replacement Pod (`cloud-services-2026-77cd8d747c-gwjbj`) within four seconds.

## Troubleshooting & Updating `index.html`

### 1. Issue Encountered

After updating `index.html` in the `Week2` directory and pushing the changes to the `main` branch on GitHub, the updated website did not automatically deploy to Rahti (`https://cloud-services-2026-week2-assignment.2.rahtiapp.fi/`), despite having configured the GitHub Webhook properly.

---

## 2. Root Cause Analysis

By inspecting the `BuildConfig` YAML configuration in Rahti, the
`spec.source.git` block was set as follows:

```yaml
source:
  type: Git
  git:
    uri: https://github.com/Jess-Xu123/cloud-services-2026.git
  contextDir: Week 2
```

**Branch mismatch:** OpenShift/Rahti defaults to monitoring the `master` branch
when no explicit `ref` field is specified under `git`.

**Event drop:** When code was pushed to GitHub's default `main` branch, GitHub
successfully sent a webhook payload for `refs/heads/main`, but Rahti ignored the
request because it was configured to listen for changes on `master`.

## 3. Solution and Steps Taken

### Step 1: Update the BuildConfig in Rahti

Added `ref: main` under `spec.source.git` in the BuildConfig YAML file:

```yaml
source:
  type: Git
  git:
    uri: https://github.com/Jess-Xu123/cloud-services-2026.git
    ref: main
  contextDir: Week 2
```

### Step 2: Update `index.html`

Modified `Week 2/index.html` to reflect the updated content, then committed
and pushed the changes to the `main` branch.

### Step 3: Verification

- **GitHub Webhooks:** Checked **Settings -> Webhooks -> Recent Deliveries** in
  GitHub and confirmed HTTP 200/201 responses after the push.
- **Rahti Builds:** Verified that a new build, such as build `#6`, was
  automatically triggered under **Builds -> Builds** in the Rahti Web Console.
- **Site Verification:** Refreshed the live endpoint and verified that the
  updated content rendered correctly:
  <https://cloud-services-2026-week2-assignment.2.rahtiapp.fi/>.

## Q&A

### Q1: Why did `oc get pods` show four Pods after scaling to three?

One of the four Pods was named `cloud-services-2026-1-build` and had a status of `Completed`. This temporary build worker assembled the Docker image. It was not an active web instance and did not consume runtime resources. The remaining three Pods were the actual running application replicas.

### Q2: Why was `https://` missing from the `oc get route` output?

The CLI output lists raw fully qualified domain names (FQDNs) in the `HOST/PORT` column to maintain clean terminal formatting. Because the route termination was configured as `edge/Redirect`, visiting the domain in a standard web browser automatically uses `https://` and secures the connection.

### Q3: How can `.DS_Store` files uploaded during Week 1 be cleaned up?

Deleting local files does not remove them from Git's remote history. Running `git rm -r --cached .DS_Store` untracks the file from the remote GitHub repository while keeping local workspace settings intact.
