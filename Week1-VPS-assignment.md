# Week 1 - VPS  Assignment

---

## Background: 
All the operations for this assignment are based on Macbook so the commands will be different than the instruction for Microsoft system.

I created my VPS into CSC cPouta. And the documented process are based on that.

### 1. Creating the VPS

- Set up CSC account using credentials, it is free for students
    - Create account on this page https://my.csc.fi/welcome, use Haka credentials to signup.
    - Login to my CSC and continue to create new project https://my.csc.fi/dashboard

- Create project
    - Create a new project following the instruction here
        - https://docs.csc.fi/accounts/how-to-create-new-project/
        - It should look like this after creating a new project
        - ![Csc new project](screenshots/csc-new-project.png)
    - Create cPouta services within your project
        - ![cPouta service](screenshots/cPouta-service.png)
        - Login to cPouta service https://pouta.csc.fi/dashboard/auth/login/?next=/dashboard/ using the Haka credentials
    - Create Virtual Machine
        - Follow the instruction here: https://docs.csc.fi/cloud/pouta/launch-vm-from-web-gui/
        - Create instance within your own project
        - ![create-VM](screenshots/create-VM.png)
        - Use Ubuntu-26 as the image when setting up VM
        - Create SSH keypair and keep it safe
        - Security group set up, open ports for SSH connection
            - 22 (SSH)
            - 80 (HTTP)
        
### 2. Connecting to the VPS with SSH

- Create a pem file to store keypair
    - `touch ~/Desktop/mykey.pem` - This will create a .pem file on desktop
    - `nano ~/Desktop/mykey.pem` - Write SSH key into .pem file
    - `mv ~/Desktop/mykey.pem ~/.ssh/csc-key.pem` - Move mykey.pem to .ssh folder
    - `chmod 400 ~/.ssh/csc-key.pem` - Restrict the key file's permission
- Connect to server
    - `ssh -i ~/.ssh/csc-key.pem ubuntu@your own public IP` - You can check the IP from Instance

### 3. Update the Linux system (Install or Update Apache)

- 

### 4. Install the Web Server

### 5. Testing the Web Server


### 6. Creating My Own Website
**bold**

### 7. Testing My Website
`Pirce of code`

### 8. Final Result

### 9. Summary