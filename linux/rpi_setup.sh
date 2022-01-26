#!/bin/bash

set -e

USERNAME=russell

# change default pi password
## passwd

# set up new user
## sudo adduser russell
## sudo usermod russell -a -G pi,adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,input,netdev,spi,i2c,gpio
## echo "russell ALL=(ALL) NOPASSWD: ALL" | sudo tee -a /etc/sudoers.d/010_russell-nopasswd

# ssh back in as russell for additional setup

# raspbian OS config
## raspi-config
# change hostname
# require network at boot
# set GPU memory to 16
# update locale and timezone
# expand filesystem
# boot latest ROM

# restart pi

# update machine
sudo apt update && sudo apt upgrade -y

# set up ssh keys
echo "Printing SSH key"
if [ ! -f ~/.ssh/id_rsa ]; then ssh-keygen -q -t rsa -N '' -f ~/.ssh/id_rsa <<<y 2>&1 >/dev/null; fi
cat ~/.ssh/id_rsa.pub
read -n 1 -r -s -p $'\nAdd key to NAS and press enter to continue...\n' </dev/tty
# allow connections to NAS
echo "Adding NAS to known_hosts"
ssh-keygen -R 10.16.8.1 && rm -rf ~/.ssh/known_hosts.old
ssh-keyscan -H 10.16.8.1 >> ~/.ssh/known_hosts

# bash aliases
echo "Create Bash aliases"
if [ ! -f ~/.bash_aliases ]; then printf "alias ls='ls -lh --color=auto'\nalias la='ls -A'\n\nalias dc='docker-compose'\n" | tee ~/.bash_aliases; fi
source ~/.bash_aliases

# set up vim
echo "Set up vim"
sudo apt install -y git vim
if [ ! -d ~/.vim_runtime ]; then git clone --depth=1 https://github.com/amix/vimrc.git ~/.vim_runtime; fi
if [ -f ~/.vim_runtime/install_awesome_vimrc.sh ]; then ~/.vim_runtime/install_awesome_vimrc.sh; else echo "ERROR: failed to set up vim"; fi
sudo -- bash -c 'if [ ! -d ~/.vim_runtime ]; then git clone --depth=1 https://github.com/amix/vimrc.git ~/.vim_runtime; fi'
sudo -- bash -c 'if [ -f ~/.vim_runtime/install_awesome_vimrc.sh ]; then bash ~/.vim_runtime/install_awesome_vimrc.sh; fi'

# set up prompt
echo "Set up Bash prompt"
curl -fsSL https://raw.githubusercontent.com/rmartin16/random/master/bash/.bash_prompt.sh -o ~/.bash_prompt
if ! grep -F ". ~/.bash_prompt" ~/.bashrc 1>/dev/null 2>&1; then printf "\nif [ -f ~/.bash_prompt ]; then\n    . ~/.bash_prompt\nfi\n" | tee -a ~/.bashrc; fi
source ~/.bash_prompt

# set up automatic updates
echo "Set up unattended upgrades"
sudo apt-get install -y unattended-upgrades
echo 'Unattended-Upgrade::Origins-Pattern {
//      Fix missing Rasbian sources.
        "origin=Debian,codename=${distro_codename},label=Debian";
        "origin=Debian,codename=${distro_codename},label=Debian-Security";
        "origin=Raspbian,codename=${distro_codename},label=Raspbian";
        "origin=Raspberry Pi Foundation,codename=${distro_codename},label=Raspberry Pi Foundation";
};' | sudo tee /etc/apt/apt.conf.d/51unattended-upgrades-raspbian

# set up NAS mounts
echo "Set up NAS mounts"
sudo apt-get -y install sshfs
sudo mkdir -p /mnt/nas/Media
sudo mkdir -p /mnt/nas/Data
echo "russell@10.16.8.1:/Media  /mnt/nas/Media  fuse.sshfs x-systemd.automount,transform_symlinks,port=5050,identityfile=/home/$USERNAME/.ssh/id_rsa,allow_other,uid=1001,gid=1001 0 0" | sudo tee -a /etc/fstab
echo "russell@10.16.8.1:/Data  /mnt/nas/Data  fuse.sshfs x-systemd.automount,transform_symlinks,port=5050,identityfile=/home/$USERNAME/.ssh/id_rsa,allow_other,uid=1001,gid=1001 0 0" | sudo tee -a /etc/fstab
sudo mount -a

# pyenv
echo "Set up pyenv"
if [ ! -d /home/$USERNAME/.pyenv ]; then curl https://pyenv.run | bash; else pyenv update; fi
if ! grep -F "/home/$USERNAME/.pyenv/bin" ~/.bashrc 1>/dev/null 2>&1; then printf '\nexport PATH="/home/$USERNAME/.pyenv/bin:$PATH"\neval "$(pyenv init -)"\neval "$(pyenv virtualenv-init -)"\n' | tee -a ~/.bashrc; fi

# install docker
echo "Set up Docker"
curl -fsSL https://get.docker.com | sudo bash
sudo usermod -aG docker $USERNAME
sudo apt-get install -y libffi-dev libssl-dev python3-dev python3 python3-pip
python3 -m pip install docker-compose

echo "Add cron jobs"
# set up regular docker clean ups
(crontab -l 2>/dev/null; echo "  0 3    *   *   *   /mnt/nas/Data/scripts/cleanup_docker.sh 2>&1 | /mnt/nas/Data/scripts/datetime_output_to_logfile.sh >> /home/$USERNAME/logs/docker_cleanup.log") | sort - | uniq - | crontab -
# set up backups
mkdir -p ~/logs
(crontab -l 2>/dev/null; echo "  0 5    *   *   *   /mnt/nas/Data/scripts/backup_to_ds1515.sh 2>&1 | /mnt/nas/Data/scripts/datetime_output_to_logfile.sh >> /home/$USERNAME/logs/backup_to_ds1515.log") | sort - | uniq - | crontab -

echo "Set up log rotation"
if ! grep -F backup_to_ds1515.log /etc/logrotate.d/mylogs 1>/dev/null 2>&1; then
echo "/home/$USERNAME/logs/backup_to_ds1515.log {
    su $USERNAME $USERNAME
    size 10M
    copytruncate
    rotate 4
    create 700 $USERNAME $USERNAME
    maxage 30
}
" | sudo tee -a /etc/logrotate.d/mylogs
fi

if ! grep -F docker_cleanup.log /etc/logrotate.d/mylogs 1>/dev/null 2>&1; then
echo "/home/$USERNAME/logs/docker_cleanup.log {
    su $USERNAME $USERNAME
    size 10M
    copytruncate
    rotate 4
    create 700 $USERNAME $USERNAME
    maxage 30
}
" | sudo tee -a /etc/logrotate.d/mylogs
fi

# manually install needrestart since debian ppa only provides v3.4 right now
echo "Install needrestart"
sudo apt install needrestart
if ! needrestart --version | grep -F "needrestart 3.5" - 1>/dev/null 2>&1; then
  SAVEPWD=$PWD
  mkdir -p ~/tmp
  cd ~/tmp
  curl -fsSL https://github.com/liske/needrestart/archive/v3.5.tar.gz | tar xz
  cd needrestart-3.5
  sudo apt-get -y install libmodule-find-perl libmodule-scandeps-perl libproc-processtable-perl libsort-naturally-perl libterm-readkey-perl libintl-perl gettext po-debconf xz-utils
  sudo make install
  # the whole reason we need v3.5...to stop false positive alerts about multiple kernels
  if ! grep -F "qr(kernel7l\.img)" /etc/needrestart/conf.d/kernel.conf 1>/dev/null 2>&1; then
    printf "# Filter kernel image filenames by regex. This is required on Raspian having\n# multiple kernel image variants installed in parallel.\n\$nrconf{kernelfilter} = qr(kernel7l\.img);\n" | sudo tee -a /etc/needrestart/conf.d/kernel.conf
  fi
  cd $SAVEPWD
fi
