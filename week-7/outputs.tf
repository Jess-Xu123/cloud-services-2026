output "public_ip" {
  value       = openstack_networking_floatingip_v2.web.address
  description = "The public floating IP address assigned to the VM."
}

output "web_url" {
  value       = "http://${openstack_networking_floatingip_v2.web.address}"
  description = "The URL to access the deployed web server."
}
