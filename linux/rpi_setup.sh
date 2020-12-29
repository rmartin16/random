# change default pi password
passwd

# set up new user
sudo adduser russell
sudo usermod russell -a -G pi,adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,input,netdev,spi,i2c,gpio
echo "russell ALL=(ALL) NOPASSWD: ALL" | sudo tee -a /etc/sudoers.d/010_russell-nopasswd

# ssh back in as russell for additional setup

# raspbian OS config
raspi-config
# change hostname
# require network at boot
# set GPU memory to 16
# update locale and timezone
# expand filesystem
# boot latest ROM

# restart

# update machine
sudo apt update && sudo apt upgrade -y

# set up ssh keys
if [ ! -f ~/.ssh/id_rsa ]; then ssh-keygen; fi && cat ~/.ssh/id_rsa.pub && read -n 1 -r -s -p $'\nAdd key to NAS and press enter to continue...\n'
# allow connections to NAS
ssh-keyscan -H 10.16.8.1 >> ~/.ssh/known_hosts

# bash aliases
printf "alias ls='ls -lh --color=auto'\nalias la='ls -A'\n\nalias dc='docker-compose'\n" | tee -a ~/.bash_aliases
source ~/.bash_aliases

# set up vim
sudo apt install -y git vim
git clone --depth=1 https://github.com/amix/vimrc.git ~/.vim_runtime && sh ~/.vim_runtime/install_awesome_vimrc.sh
# repeat for root with sudo -i

# set up prompt
curl -fsSL https://raw.githubusercontent.com/rmartin16/random/master/bash/.bash_prompt.sh -o ~/.bash_prompt
printf "\nif [ -f ~/.bash_prompt ]; then\n    . ~/.bash_prompt\nfi\n" | tee -a ~/.bashrc && source ~/.bash_prompt

# set up automatic updates
sudo apt-get install -y unattended-upgrades
echo 'Unattended-Upgrade::Origins-Pattern {
//      Fix missing Rasbian sources.
        "origin=Debian,codename=${distro_codename},label=Debian";
        "origin=Debian,codename=${distro_codename},label=Debian-Security";
        "origin=Raspbian,codename=${distro_codename},label=Raspbian";
        "origin=Raspberry Pi Foundation,codename=${distro_codename},label=Raspberry Pi Foundation";
};' | sudo tee /etc/apt/apt.conf.d/51unattended-upgrades-raspbian

# manually install since debian ppa only provides v3.4 right now
SAVEPWD=$PWD
mkdir -p ~/tmp
cd ~/tmp
curl -fsSL https://github.com/liske/needrestart/archive/v3.5.tar.gz | tar xz
cd needrestart-3.5
sudo apt-get -y install libmodule-find-perl libmodule-scandeps-perl libproc-processtable-perl libsort-naturally-perl libterm-readkey-perl libintl-perl gettext po-debconf xz-utils
sudo make install
# the whole reason we need v3.5...to stop false positive alerts about multiple kernels
printf "# Filter kernel image filenames by regex. This is required on Raspian having\n# multiple kernel image variants installed in parallel.\n\$nrconf{kernelfilter} = qr(kernel7l\.img);\n" | sudo tee -a /etc/needrestart/conf.d/kernel.conf
cd $SAVEPWD

# set up NAS mounts
sudo apt-get -y install sshfs
sudo mkdir -p /mnt/nas/Media
sudo mkdir -p /mnt/nas/Data
echo "russell@10.16.8.1:/Media  /mnt/nas/Media  fuse.sshfs x-systemd.automount,transform_symlinks,port=5050,identityfile=/home/russell/.ssh/id_rsa,allow_other,uid=1001,gid=1001 0 0" | sudo tee -a /etc/fstab
echo "russell@10.16.8.1:/Data  /mnt/nas/Data  fuse.sshfs x-systemd.automount,transform_symlinks,port=5050,identityfile=/home/russell/.ssh/id_rsa,allow_other,uid=1001,gid=1001 0 0" | sudo tee -a /etc/fstab
sudo mount -a

# pyenv
curl https://pyenv.run | bash
printf '\nexport PATH="/home/russell/.pyenv/bin:$PATH"\neval "$(pyenv init -)"\neval "$(pyenv virtualenv-init -)"\n' | tee -a ~/.bashrc

# install docker
curl -fsSL https://get.docker.com | sudo bash
sudo usermod -aG docker russell
sudo apt-get install -y libffi-dev libssl-dev python3-dev python3 python3-pip
python3 -m pip install docker-compose
# set up regular clean ups
printf "  0 3    *   *   *   /mnt/nas/Data/scripts/cleanup_docker.sh 2>&1 | /mnt/nas/Data/scripts/datetime_output_to_logfile.sh >> /home/russell/logs/docker_cleanup.log" | sudo tee -a /etc/cron.d/cleanup _docker

# set up backups
mkdir -p ~/logs
printf "  0 5    *   *   *   /mnt/nas/Data/scripts/backup_to_ds1515.sh 2>&1 | /mnt/nas/Data/scripts/datetime_output_to_logfile.sh >> /home/russell/logs/backup_to_ds1515.log" | sudo tee -a /etc/cron.d/backup_to_ds1515
