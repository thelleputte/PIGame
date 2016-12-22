#! /bin/bash

echo 1 > /sys/class/gpio/gpio$1/value

if [$1 = 15]
	echo "player1 button"
elif [$1 = 27] 
	echo "player2 button"
elif [$1 = 16]
	echo "nack button"
elif [$1 =19]
	echo "nack button"
fi

sleep(0.4) #stay pressed for about 1/2 second
#release the button 
echo 0 > /sys/class/gpio/gpio$1/value