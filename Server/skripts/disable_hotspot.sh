 #!/bin/sh
# script for disabling hotspot for filebrowser
 

if grep --quiet "^ *# *denyinterfaces wlan0" /etc/dhcpcd.conf; then
  echo "hotspot is allready disabled"
  exit 1
fi

 sed -i -e 's/^ *denyinterfaces wlan0/#denyinterfaces wlan0/g' /etc/dhcpcd.conf

 sudo rfkill unblock wifi
 sudo dhcpcd --allowinterfaces wlan0
 sudo killall hostapd
 sudo killall dnsmasq
 sudo ifconfig wlan0 0.0.0.0
 sudo sh -c "echo | iptables-restore"
 sudo sh -c "echo 0 > /proc/sys/net/ipv4/ip_forward"
 sudo iwlist wlan0 scan > /dev/null 2>&1
 sudo ifconfig wlan0 up
 sudo systemctl restart avahi-daemon
 sudo wpa_cli -i wlan0 reconnect
 sudo reboot
