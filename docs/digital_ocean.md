# Pre-Installation
Here\'s what **you need to setup** for our application to run smoothly the first time you want to setup a new [Digital Ocean](https://m.do.co/c/b761e5fdd694 "Digital Ocean") server (droplet) node:

During your node creation screen, Copy the box below and edit the information to use inside the \"User Data\" box.
- Customize the username: We have pre-filled `serviceharmony` as our username suggestion but anything other than **root** works here!
- Add your own ssh-rsa public key in place of the ssh-rsa example key below.

```bash
#cloud-config
users:
  - name: serviceharmony
    groups: sudo
    shell: /bin/bash
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    ssh-authorized-keys:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAA_EXAMPLE_KEY_ONLY_OOHch79N5OnB136TaVdXPQFaYFzubA1Lzbeus5H2BcbMieDyGBBTh4gEEkz2hsGCXeaw==
package_upgrade: true
packages:
 - dnsutils
 - nethogs
 - python3-pip
```

Return to the [main README.md file](https://github.com/easy-node-one/validator-toolbox/blob/main/README.md).