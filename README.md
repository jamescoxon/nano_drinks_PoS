# nano_drinks_PoS
A simple combination of scripts that monitor a nano address and when funds are received distribute them (and return change). Used in Nigeria for selling soft drinks for Nano!

## Real life setup
* We have installed a drinks fridge in a Student Hostel at the Uni of Benin in Nigeria, you can buy soft drinks for small amounts of Nano (currently 0.2XNO), often people will collect Nano using the WeNano app (https://wenano.net). This bot helps the host collect Nano and uses whatsapp to inform them about transactions - whatsapp is chosen as is most popular in this area (despite being technically more challenging) to ensure the easiest adoption possible.

## Components
* Whatsapp communication is provided by whatsapp-js which uses puppetter. Using express framework and node.js the app.js script creates a simple http server which acts as an api between the whatsapp system and the bot
* main_bot.py is a python script that monitors an address (by polling a node - you may need to adjust the timing or speak with a public node operator as will likely exceed the usage limits) and when funds are received manages them (splits the funds between host and supplier and will return change or refund if too little is sent). 
