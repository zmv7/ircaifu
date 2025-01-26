# ircaifu - An IRC bot with Ollama integration

## Installation

1. Install the necessary libraries (you likely will need to use venv):
   
       pip install miniirc ollama

3. Edit `ircaifu.ini` file to meet your requirements.
   
4. Run the `ircaifu.py` script:

       python3 ./ircaifu.py 

## Usage
Once connected and joined the channel, you can use it from your account  
  
Mention a bot to ask it. E.g. `Ircaifu: Hello, introduce yourself`
  
Available commands for admins:
* `!join <chan1[,chan2]> [key1,key2]` - join the channel(s)
* `!part <chan1[,chan2]> [message]` - leave the channel(s)
* `!getmodel` - get the name of current ollama model
* `!setmodel <model> [nick]` - set the ollama model, with new nickname optionally
* `!nick <nick>` - set the new nickname
* `!reset` - reset the ollama context
* `!quote <QUOTE>` - execute IRC quote

## ircaifu.ini
```ini
[Main]
nick = Ircaifu
model = llama3.1
host = irc.libera.chat
port = 6697
channels = #ircaifu   #comma-separated channels to join when connecting
admins = Zemtzov7    #comma-separated nicknames
```
