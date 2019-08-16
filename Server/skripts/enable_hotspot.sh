 #!/bin/sh
 # script for starting hotspot 
BASE_IP="172.24.1"

if grep --quiet "^ *denyinterfaces wlan0" /etc/dhcpcd.conf; then
  echo "hotspot is allready enabled"
  exit 1
fi

 sed -i -e 's/^ *# *denyinterfaces wlan0/denyinterfaces wlan0/g' /etc/dhcpcd.conf




 SKRIPTPATH="$PWD"
 
 sudo rfkill unblock wifi
 sudo wpa_cli -i wlan0 disconnect
 sudo dhcpcd --denyinterfaces wlan0
 sudo ifconfig wlan0 down
 sudo ifconfig wlan0 $BASE_IP.1 netmask 255.255.255.0 broadcast $BASE_IP.255
 sudo killall dnsmasq
 sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
 sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
 sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
 sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
# sudo dnsmasq --conf-file="$SKRIPTPATH/dnsmasq.conf"
 (sleep 15 && sudo systemctl restart avahi-daemon) &
 sudo nohup /usr/sbin/hostapd $SKRIPTPATH/hostapd.conf > /dev/null 2>&1 &
 sudo reboot
