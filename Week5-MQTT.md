# Week 5 - Setup and Testing of an MQTT Broker with TLS on Linux (cPouta)

## Overview

This document covers the installation, configuration, remote testing, and TLS encryption setup for a Mosquitto MQTT Broker running on an OpenStack cloud instance (cPouta) using a MacBook Pro M1 client.

## Concepts and practices

### Concepts and Real-World Industry Application

#### What is MQTT and Why Do We Use It?

MQTT (Message Queuing Telemetry Transport) is a lightweight messaging protocol designed for constrained devices and low-bandwidth, high-latency networks.

Think of MQTT like a school PA system / radio station:

- **Publisher:** The person speaking into the microphone (e.g., a smart temperature sensor).

- **Subscriber:** The listener tuned into a specific radio channel (e.g., a mobile app displaying temperature).

- **Broker (Mosquitto):** The radio station broadcasting center that receives messages from publishers and routes them to subscribers.

#### Why Deploy on a Cloud Server (cPouta)?

In IoT applications (such as smart homes, connected vehicles, or industrial telemetry), devices are geographically distributed. They cannot connect directly to a local developer laptop. Hosting the broker on a cloud platform with a public IP address ensures global accessibility.

- **Unencrypted vs. Encrypted Traffic:** In commercial environments, plain TCP (Port 1883) is strictly prohibited for public-facing traffic. All production telemetry is forced through TLS/SSL (Port 8883).

- **Certificates:** While self-signed certificates are used in testing, production systems use certificates issued by trusted Certificate Authorities (CAs) like Let's Encrypt, or burn unique client certificates onto hardware devices during manufacturing.

- **Network Security:** Production brokers sit behind cloud Security Groups and network firewalls. Port 1883 is closed to the internet, leaving only 8883 accessible.

## 2. System Architecture Flowchart

```text
+---------------------------------------------------------------------------------+
|                                MacBook Pro M1 (Local)                           |
|                                                                                 |
|   [Terminal 1: Subscriber]                           [Terminal 2: Publisher]    |
|   mosquitto_sub -h 86.50.231.121                   mosquitto_pub -h 86.50.231.121  |
|                 -p 8883 --cafile ca.crt                          -p 8883          |
|                 --insecure -t test/topic                         --cafile ca.crt  |
|                 (Listening...)                                   --insecure       |
|                                                                  -m "Hello"       |
+-----------------------|-----------------------------------------|---------------+
                        |                                         |
                        | 1. TLS 8883 Encrypted Sub               | 2. TLS 8883 Encrypted Pub
                        v                                         v
+---------------------------------------------------------------------------------+
|                                 cPouta Cloud Platform                           |
|                                                                                 |
|   [Security Group] -> Ingress Rules: TCP 1883 & TCP 8883 Allowed                |
|                                      |                                          |
|                                      v                                          |
|   [cPouta Linux VM Server (Mosquitto Broker)]                                   |
|   ├── Certificate Storage: /etc/mosquitto/certs/ (mosquitto:mosquitto)          |
|   └── Configuration File: /etc/mosquitto/mosquitto.conf                         |
|         ├── listener 1883 / allow_anonymous true                                |
|         └── listener 8883 / cafile ... / certfile ... / keyfile ...             |
+---------------------------------------------------------------------------------+
```

## 3. Step-by-Step Implementation and Troubleshooting Log

### Phase 1: Local VM Installation and Testing

#### SSH Connection to Cloud VM

Set the correct private key permissions and log in:

```bash
chmod 400 ~/.ssh/csc-key.pem
ssh -i ~/.ssh/csc-key.pem ubuntu@86.50.231.121
```

> (Note: Storing keys in ~/.ssh/ with 400 permissions is standard UNIX security practice).

#### Install Mosquitto Broker and Clients

```bash
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

#### Verify Local Functionality

- **Terminal 1 (Subscriber):** `mosquitto_sub -h localhost -t test/topic`

- **Terminal 2 (Publisher):** `mosquitto_pub -h localhost -t test/topic -m "Hello MQTT!"`

### Phase 2: Remote Access Configuration (Port 1883)

#### Modify Broker Configuration

Edit /etc/mosquitto/mosquitto.conf to bind Mosquitto to external interfaces:

```text
listener 1883
allow_anonymous true
```

Apply Linux firewall rule and restart the daemon:

```bash
sudo ufw allow 1883
sudo systemctl restart mosquitto
```

#### Configure Cloud Security Group (cPouta)

Add an Ingress rule in the cPouta Web Console under Network -> Security Groups:

- **Direction:** Ingress
- **Protocol:** TCP
- **Port:** 1883
- **CIDR:** 0.0.0.0/0

#### Test Remote Connectivity from macOS

Verify port accessibility from the M1 Mac terminal:

```bash
nc -zv -w 5 86.50.231.121 1883
```

Run multi-terminal pub/sub test:

- **Mac Terminal 1:** `mosquitto_sub -h 86.50.231.121 -p 1883 -t test/topic`

- **Mac Terminal 2:** `mosquitto_pub -h 86.50.231.121 -p 1883 -t test/topic -m "Message from M1 Mac"`

### Phase 3: TLS Encryption Setup (Port 8883)

#### Update Cloud Security Group

Add a second Ingress rule for the secure port:

- **Direction:** Ingress
- **Protocol:** TCP
- **Port:** 8883
- **CIDR:** 0.0.0.0/0

#### Generate TLS Certificates via OpenSSL (On Linux VM)

```bash
openssl genrsa -out ca.key 2048
openssl req -new -x509 -days 365 -key ca.key -out ca.crt
openssl genrsa -out server.key 2048
openssl req -new -out server.csr -key server.key
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365

sudo mkdir -p /etc/mosquitto/certs
sudo cp ca.crt server.crt server.key /etc/mosquitto/certs/
```

#### Update Mosquitto Configuration

Append TLS configuration to /etc/mosquitto/mosquitto.conf:

```text
listener 1883
allow_anonymous true

listener 8883
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key
require_certificate false
allow_anonymous true
```

#### Resolve Certificate File Permission Error

**Issue Identified:** Running `sudo systemctl restart mosquitto` failed. Direct binary invocation (`mosquitto -c /etc/mosquitto/mosquitto.conf`) revealed: Unable to load server key file... Permission denied.

**Root Cause:** Certificate files were created by root, while the Mosquitto service process runs under the unprivileged mosquitto system user.

**Resolution:**

```bash
sudo chown -R mosquitto:mosquitto /etc/mosquitto/certs/
sudo chmod 600 /etc/mosquitto/certs/server.key
sudo chmod 644 /etc/mosquitto/certs/ca.crt
sudo chmod 644 /etc/mosquitto/certs/server.crt
sudo ufw allow 8883
sudo systemctl restart mosquitto
```

#### Download CA Certificate to macOS Client

Run from local M1 Mac terminal:

```bash
scp -i ~/.ssh/csc-key.pem ubuntu@86.50.231.121:/etc/mosquitto/certs/ca.crt ~/Downloads/
```

#### Execute Encrypted Pub/Sub Test

Mac Terminal 1 (Subscriber):

```bash
mosquitto_sub -h 86.50.231.121 -p 8883 --cafile ~/Downloads/ca.crt --insecure -t test/topic
```

**Mac Terminal 2 (Publisher):**

```bash
mosquitto_pub -h 86.50.231.121 -p 8883 --cafile ~/Downloads/ca.crt --insecure -t test/topic -m "Secure message from M1 Mac"
```

> (Note: `--insecure` is required to bypass hostname verification against self-signed IP-based certificates).
