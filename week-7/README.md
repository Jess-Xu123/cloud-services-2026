# OpenTofu Web Server Infrastructure on CSC cPouta

This project provisions an automated, secure Apache Web Server instance on the **CSC cPouta (OpenStack)** cloud using **OpenTofu**.

---

## 📋 Prerequisites

Before running this project, ensure you have the following installed and configured:

1. **OpenTofu** (v1.6.0+ or compatible Terraform version)
2. **OpenStack OpenRC / Cloud Credentials** (`clouds.yaml` or an OpenRC authentication script from cPouta)
3. An active **SSH Keypair** locally (e.g., `~/.ssh/id_ed25519.pub`)

---

## 🚀 Getting Started

Follow these steps to deploy the infrastructure:

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd week-7
```

### 2. Configure Credentials

Set your OpenStack cloud environment variable (matching the cloud entry in your <code>clouds.yaml</code>):

```bash
export OS_CLOUD=openstack
```

### 3. Create Variable Values File

Copy the example variable file and populate it with your own project configuration:
Edit <code>terraform.tfvars</code> with your details:

```bash
cp terraform.tfvars.example terraform.tfvars
```

---

## 🛠️ OpenTofu Execution Pipeline

### 1. Initialize OpenTofu

Download and initialize provider plugins:

```bash
tofu init
```

### 2. Validate Configuration

Check for syntax and configuration errors:

```bash
tofu validate
```

### 3. Preview Deployment Plan

Generate and inspect the resource execution plan:

```bash
tofu plan
```

### 4. Deploy Infrastructure

Apply the configuration to create the OpenStack resources (VM, Floating IP, Port, Security Groups, Keypair):

```bash
tofu apply
```

---

## 🌐 Verification & Access

Once tofu apply completes successfully, OpenTofu will print the output variables:

### 1. Access Web Page:

Open the web_url printed in the terminal (e.g., http://<PUBLIC_IP>) in your web browser.

### 2. SSH into VM:

```bash
ssh -i ~/.ssh/id_ed25519 ubuntu@<PUBLIC_IP>
```
