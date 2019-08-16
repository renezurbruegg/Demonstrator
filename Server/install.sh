#!/bin/bash

 USER_HOME=$(getent passwd $SUDO_USER | cut -d: -f6)
 PASSWORD="pale2str"
 HOSTNAME="demonstrator"
 SKRIPTPATH="$PWD/$(dirname $0)"
 BASE_IP="172.24.1"

if [ "$EUID" -ne 0 ]
   then echo "Please run as root"
   exit
 fi

 if ! ping -q -c 1 -W 1 google.com >/dev/null 2>&1; then
   echo "Make sure to have a working Network Connection!"
   exit
 fi


 #changing hostname
 raspi-config nonint do_hostname $HOSTNAME

 echo "---------------------- enabling auto login --------------------------"

 #changing to autologin
 systemctl set-default multi-user.target
 sed /etc/systemd/system/autologin@.service -i -e "s#^ExecStart=-/sbin/agetty --autologin [^[:space:]]*#ExecStart=-/sbin/agetty --autologin $SUDO_USER#"


 ln -fs /etc/systemd/system/autologin@.service /etc/systemd/system/getty.target.wants/getty@tty1.service

 echo "---------------------- changing locale and timezone ----------------------  "

 #change locale
 LOCALE_LINE="de_CH.UTF-8 UTF-8"
 LOCALE="$(echo $LOCALE_LINE | sed 's/ .*//')"
 echo "$LOCALE_LINE" > /etc/locale.gen
 sed -i "s/^\s*LANG=\S*/LANG=$LOCALE/" /etc/default/locale
 dpkg-reconfigure -f noninteractive locales

 #change timezone
 TIMEZONE="Europe/Zurich"

 rm /etc/localtime
 echo "$TIMEZONE" > /etc/timezone
 dpkg-reconfigure -f noninteractive tzdata

 #change keyboard
 KEYMAP="ch"
 sed -i /etc/default/keyboard -e "s/^XKBLAYOUT.*/XKBLAYOUT=\"$KEYMAP\"/"
 dpkg-reconfigure -f noninteractive keyboard-configuration
 invoke-rc.d keyboard-setup start
 setsid sh -c 'exec setupcon -k --force <> /dev/tty1 >&0 2>&1'
 udevadm trigger --subsystem-match=input --action=change


 echo "----------------------  changing GL Driver  ---------------------- "
 #change GL Driver
 CONFIG="/boot/config.txt"
 sed $CONFIG -i -e "s/^dtoverlay=vc4-kms-v3d/#dtoverlay=vc4-kms-v3d/"
 sed $CONFIG -i -e "s/^#dtoverlay=vc4-fkms-v3d/dtoverlay=vc4-fkms-v3d/"
 if ! grep -q -E "^dtoverlay=vc4-fkms-v3d" $CONFIG; then
   printf "dtoverlay=vc4-fkms-v3d\n" >> $CONFIG
 fi

 echo "----------------------  updating system and installing necessary software ---------------------- "
 #updating system and installing necessary software
 apt -y update
 apt -y upgrade

 apt-get install -y install xinit xdotool chromium-browser git python-smbus i2c-tools rpi.gpio python3-venv python3-pip  python-dev lighttpd unclutter unzip pijuice-base
echo " ----------------------  Installing backend requirements ---------------------- "

(echo "raspberry" ; echo "$PASSWORD" ; echo "$PASSWORD") | passwd
echo "  ----------------------   Enabling I2C and SPI  ----------------------  "

raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0

echo "----------------------  starting ssh ---------------------- "

systemctl enable ssh
systemctl start ssh

 echo "----------------------  writing init file for x-server ---------------------- "
 #writing init file for x-server
 cat <<EOF > $USER_HOME/.xinitrc
 #! /bin/sh

 xset s off
 xset s noblank
 xset -dpms

 unclutter &
chromium-browser --kiosk  --ap http://127.0.0.1:80 --window-position=0,0 --window-size=800,480
--start-fullscreen --incognito --noerrdialogs --disable-translate --no-first-run --fast --fast-start --disable-infobars --disable-features=TranslateUI
EOF

pip3 install -r  $SKRIPTPATH/backend/requirements.txt

chmod +x $SKRIPTPATH/backend/run.py
# Auto start flask server

sed -i "/^exit 0/i python3 $SKRIPTPATH/backend/run.py 2>$SKRIPTPATH/server.log &" /etc/rc.local
#  #make hotspot scripts executable
#  chmod a+x
# $USER_HOME/tesla/application/filebrowser/enable_wifi_hotspot.sh
#  chmod a+x
# $USER_HOME/tesla/application/filebrowser/disable_wifi_hotspot.sh

#  #rotate lcd and add splashscreen
#  echo "lcd_rotate=2" >> /boot/config.txt
#  sed -i '$ s/$/ quiet splash plymouth.ignore-serial-consoles/'
# /boot/cmdline.txt
#  cp $USER_HOME/tesla/splashscreen/splashscreen.png
# /usr/share/plymouth/themes/pix/splash.png
#  sed -i '/message_sprite.SetImage(my_image);/s/^/#/g'
# /usr/share/plymouth/themes/pix/pix.script

#  #adding Application and X-Server start on boot
#  echo "sudo /home/pi/tesla/application/teslaapplication &>/dev/null
# &" >> $USER_HOME/.bashrc

echo "startx -- -nocursor &>/dev/null" >> $USER_HOME/.bashrc



#setup hotspot

sudo systemctl stop hostapd
sudo systemctl stop dnsmasq
echo " Setting up hotspot configuration"



if grep --quiet "denyinterfaces wlan0" /etc/dhcpcd.conf; then
  echo "hotspot allready configured"
  exit 1
fi




echo "#denyinterfaces wlan0" >> /etc/dhcpcd.conf
echo "allow-hotplug wlan0" >> /etc/network/interfaces

cat >/etc/network/interfaces.d/wlan0 <<EOL
auto wlan0
iface wlan0 inet static
  address $BASE_IP.1
  netmask 255.255.255.0
  network $BASE_IP.0
  broadcast $BASE_IP.255
EOL


service dhcpcd restart
ifconfig wlan0 down
ifconfig wlan0 up

cp $SKRIPTPATH/hostapd.conf /etc/hostapd.hostapd.conf

sed -i -e 's:#DAEMON_CONF="[^\n ]*":DAEMON_CONF="/etc/hostapd/hostapd.conf":g' /etc/default/hostapd
mv /etc/dnsmasq.conf /etc/dnsmasq.conf.bak
touch /etc/dnsmasq.conf
cat >/etc/network/interfaces.d/wlan0 <<EOL
interface=wlan0      # Use interface wlan0
listen-address=$BASE_IP.1 # Explicitly specify the address to listen on
bind-interfaces      # Bind to the interface to make sure we aren't sending things elsewhere
server=8.8.8.8       # Forward DNS requests to Google DNS
domain-needed        # Don't forward short names
bogus-priv           # Never forward addresses in the non-routed address spaces.
dhcp-range= $BASE_IP.50,$BASE_IP.150,12h # Assign IP addresses with a 12 hour lease time
EOL

sed -i "/^exit 0/i iptables-restore < /etc/iptables.ipv4.nat" /etc/rc.local



reboot
