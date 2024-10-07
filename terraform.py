module "vault" {
  source            = "git::https://github.com/Equifax/6507_US_DEVOPS_B2C_AWS_CSA_HASHICORP_VAULT"
  vault_address     = var.vault_address
  vault_namespace   = var.vault_namespace
  vault_secret_path = var.vault_secret_path
}

resource "null_resource" "s3-backup" {
  triggers = {
    always_run = timestamp() // Forces the resource to run every time.
  }

  connection {
    type        = "ssh"
    host        = data.aws_instance.ec2_instance.private_ip
    user        = "ec2-user"  // Static user for the EC2 instance
    password    = module.vault.vault_data["token"]  // Using token for authentication
    port        = "22"
    script_path = "/export/home/${module.vault.vault_data["username"]}/terraform_%RAND%.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo mount -o remount,exec /tmp",
      "sudo mkdir -p /tmp/${var.instance_name}/",
      "sudo chmod -R 777 /tmp/${var.instance_name}/",
      "cd /tmp/${var.instance_name}/",
      "sudo rm -rf /tmp/${var.instance_name}/*",
      "sudo rpm -qa > yum_packages",
      "ROOT=$(findmnt -o UUID | tail -n1) && cat /etc/fstab | grep -v $ROOT >> fstab",
      "export UGIDLIMIT=400",
      "sudo awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3<=65534)' /etc/passwd > ./passwd",
      "sudo awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3<=65534)' /etc/group > ./group",
      "sudo awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3<=65534) {print $1}' /etc/passwd | sudo egrep -f - /etc/shadow > ./shadow",
      "sudo cp -p /etc/gshadow .",
      "sudo cp -prf /etc/sudoers.d .",
      "sudo cp -p /etc/nslcd.conf .",
      "sudo cp -p /etc/security/limits.conf .",
      "sudo cp -p /etc/crontab .",
      "sudo cp -prf /var/spool/cron .",
      "sudo tar -czvf /tmp/${var.instance_name}-backup.tar.gz .",
      "sudo chmod 755 /tmp/${var.instance_name}-backup.tar.gz",
      "aws s3 cp /tmp/${var.instance_name}-backup.tar.gz s3://${var.s3_bucket}/b2c/brm/${var.instance_name}-backup.tar.gz"
    ]
  }
}
