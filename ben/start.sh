#! /bin/bash

#configure pull_ups
#no pull on outputs 
sudo pull_config/pull_config 0x00 0x00420A50 0
#pull up on inputs
sudo pull_config/pull_config 0x02 0x02855000 0
#pull up on ack/nack
sudo pull_config/pull_config 0x02 0x04100000 0
#no pull on 16 & 19 & 27 for future use for nack/ack emulation
sudo pull_config/pull_config 0x00 0x08090000 0

#export emulated gpios
sudo echo 15 > /sys/class/gpio/export #for player emulation
#sudo echo 27 > /sys/class/gpio/export #for player2 emulation
sudo echo 19 > /sys/class/gpio/export #for ack_emulation
sudo echo 16 > /sys/class/gpio/export #for  nack_emulation

#configure inputs
#player pins auto configured by python routine

#first player pin emulation GPIO15
sudo echo "out" > /sys/class/gpio/gpio15/direction
sudo echo 1 > /sys/class/gpio/gpio15/active_low
sudo echo 0 > /sys/class/gpio/gpio15/value

#second player pin emulation GPIO27
#sudo echo "out" > /sys/class/gpio/gpio27/direction
#sudo echo 1 > /sys/class/gpio/gpio27/active_low
#sudo echo 0 > /sys/class/gpio/gpio27/value

#ack pin emulation GPIO19
sudo echo "out" > /sys/class/gpio/gpio19/direction
sudo echo 1 > /sys/class/gpio/gpio19/active_low
sudo echo 0 > /sys/class/gpio/gpio19/value

#nack pin emulation GPIO16
sudo echo "out" > /sys/class/gpio/gpio16/direction
sudo echo 1 > /sys/class/gpio/gpio16/active_low
sudo echo 0 > /sys/class/gpio/gpio16/value

#ready to start
sudo python3 piGame.py