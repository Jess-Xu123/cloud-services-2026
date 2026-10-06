variable "student_name" {
  description = "Name of the student for this week7 assignment"
  type        = string

  validation {
    condition     = length(var.student_name) > 0
    error_message = "Student name must not be empty"
  }
}

variable "page_message" {
  description = "Custom message displayed on the web page, can be changed later."
  type        = string
  default     = "Update experiment message 1!"
}

variable "name_prefix" {
  description = "Prefix used for naming OpenStack resources to avoid collisions."
  type        = string
  default     = "zhaohuixu-VM"
}

variable "project_network" {
  description = "The project network name in CSC."
  type        = string
  default     = "project_2020475"
}

variable "image_name" {
  description = "The Linux image name to use for VM."
  type        = string
  default     = "Ubuntu-22.04"
}

variable "flavor_name" {
  description = "The flavor (CPU/RAM size) for the VM."
  type        = string
  default     = "standard.tiny"
}

variable "ssh_public_key_path" {
  description = "Local path to SSH public key."
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "ssh_allowed_cidr" {
  description = "IP address range allowed for SSH access (Public IP with /32)"
  type        = string

  validation {
    condition     = can(cidrnetmask(var.ssh_allowed_cidr))
    error_message = "Must be a valid IPv4 CIDR string, e.g., '192.0.2.1/32'."
  }

}