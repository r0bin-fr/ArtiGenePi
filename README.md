# artigene
The aim of this project is to use Artisan roasting scope software (https://artisan-roasterscope.blogspot.com/) with a Gene Cafe CBR 101 (Coffee roaster, http://genecafe.com/) using a Raspberry Pi3, in order to enhance the roasting process and have more control on it. 

This implies realisation of a Bluetooth temperature sensor located in the drum, battery powered (inspired from www.roasthacker.com), make Raspberry get the temperature remotely, then pass it to Artisan roaster software through local network socket. 

In addition, I use an SSR on the heater in order to be able to dim the heat power for an optimal roasting process (during first crack for example). Also, i use a L293D chipset to control the drum motor in order to reduce the drum speed and get more accurate readings.

- main.py: program that get the temperature from BT sensor and makes it available to a local socket
- multithreadBT.py: task that handle bluetooth connection (retry on error) and update current temperature
- multithreadMotor.py: to control the motor speed (when speed control is activated)
- readBT.py: python class that help to store and access temperature data
- client.py: program called by Artisan. it connects to the socket and retrieves temperature, then prints it once (called each second by Artisan)

More info on the project here: 
http://expresso.cultureforum.net/t12319-utiliser-la-gene-cafe-avec-artisan-le-roaster-connecte or http://expresso.1fr1.net/t12319-utiliser-la-gene-cafe-avec-artisan-le-roaster-connecte

