# artigene
This project is to make Artisan work for Gene Cafe CBR 101 (Coffee roaster) using a Raspberry Pi3. 

This implies realisation of a Bluetooth temperature sensor (inspired from www.roasthacker.com) and make Raspberry get the temperature remotely, then pass it to Artisan roaster software through local socket. 

In addition, I put an SSR to be able to dim the heat power, for an optimal roasting process.

- main.py: program that get the temperature from BT sensor and makes it available to a local socket
- multithreadBT.py: task that handle bluetooth connection (retry on error) and update current temperature
- readBT.py: python class that help to store and access temperature data
- client.py: program called by Artisan. it connects to the socket and retrieves temperature, then prints it once (called each second by Artisan)

More info here: 
http://expresso.cultureforum.net/t12319-utiliser-la-gene-cafe-avec-artisan-le-roaster-connecte

