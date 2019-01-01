# First you have to run sudo raspi-config and
# - Enable SSH
# - Enable 1-Wire
# - Adapt Hostname
# - Adapt Keyboard Layout
# - Adapt Password


# Then you have to mound the Usb stick by running
# sudo blkid -o list -w /dev/null
# and add following line at the end of /etc/fstab
# UUID=<Your Device UUID, e.g. B624-79FF> /media/mainusb/ vfat utf8,uid=pi,gid=pi,noatime 0

echo "Installing required software..."
sudo apt update
sudo apt install git python-pip python3-pip python-mysqldb tmux
echo "done"

echo "Installing required python packages..."
pip2 install -r requirements.txt
echo "done"

