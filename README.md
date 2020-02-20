# family-frame
A raspberry pi based frame to display family photos

## Preparation
### Open lightdm conf
> sudo nano /etc/lightdm/lightdm.conf

Modify line

> xserver-command=X -s 0 dpms

### Update & installation of feh
```
sudo apt-get update
sudo apt-get install feh
sudo apt-get install gnome-schedule

```
### Contrab conf

```
# Launch photo display, every 30mn
# */30 * * * * bash /home/pi/Documents/dynamicFrame/frame.sh

# Downloading new photos, every 2 minutes
# */2 * * * * cd /home/pi/Documents/dynamicFrame/ && python dynamicFrame_04.py

# Starting display at reboot
# @reboot bash /home/pi/Documents/dynamicFrame/frame.sh

# Rebooting every hour to avoid screen freeze
# 0 * * * * sudo reboot

# Every day, shutting down at 11PM
# 30 22 * * * sudo shutdown -h now
``

