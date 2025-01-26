import miniirc
import ollama
import re
import os
import textwrap
import configparser
import sys

cfgfile = "ircaifu.ini"
config = configparser.ConfigParser()
config.read(cfgfile)

nick = config.get("Main", "nick")
model = config.get("Main", "model")
host = config.get("Main", "host")
port = int(config.get("Main", "port"))
channels = config.get("Main", "channels").split(",")
admins = config.get("Main", "admins").split(",")

if not (nick and model and host and port and channels):
	print("Incorrect config file")
	exit

def saveconf():
	config["Main"]["nick"] = nick
	config["Main"]["model"] = model
	with open(cfgfile, "w") as file:
		config.write(file)

irc = miniirc.IRC(host, port, nick, channels)

blacklist = [
	"NickServ",
	"ChanServ",
	"Auth",
]

chat = []

@miniirc.CmdHandler('PRIVMSG', 'NOTICE', 'NAMES', colon=False)
def cmdhandler(irc, command, hostmask, args):
	if not args:
		return
	global chat, nick, model
	target = args[0] == nick and hostmask[0] or args[0]
	user = hostmask[0]
	relay_match = re.match(r"^<([\w@]+)> ", args[1])
	if relay_match:
		user = relay_match.group(1)
		args[1] = args[1][relay_match.end():]

	if target in blacklist or user in blacklist:
		return

	if args[1].startswith((nick+", ",nick+": ")):
		msg = re.sub(nick + ". ", "", args[1])
		if not msg.strip():
			return
		if msg.startswith("!"):
			if not hostmask[1] in admins:
				irc.send("PRIVMSG", target, "Insufficient privileges!")
				return
			cmdwp = msg.split()
			cmd, params = cmdwp[0], cmdwp[1:]
			match cmd:
				case "!help":
					hints = [
						"Available commands:",
						"!join <chan1[,chan2]> [key1,key2]",
						"!part <chan1[,chan2]> [message]",
						"!getmodel",
						"!setmodel <model> [nick]",
						"!nick <nick>",
						"!reset",
						"!quote <QUOTE>"
					]
					for hint in hints:
						irc.send("PRIVMSG", target, hint)
				case "!join" if len(params) > 0:
					irc.quote("JOIN "+" ".join(params))
					irc.send("PRIVMSG", target, "Attempted to join "+params[0])
				case "!part" if len(params) > 0:
					irc.quote("PART "+" ".join(params))
					irc.send("PRIVMSG", target, "Attempted to part "+params[0])
				case "!setmodel" if len(params) > 0:
					model = params[0]
					if len(params) > 1:
						nick = params[1]
						irc.quote("NICK "+nick)
					chat = []
					irc.send("PRIVMSG", target, "Model has been set to "+model)
					saveconf()
				case "!getmodel":
					irc.send("PRIVMSG", target, "Current model is "+model)
				case "!nick" if len(params) > 0:
					if params[0]:
						nick = params[0]
						irc.quote("NICK "+nick)
					saveconf()
				case "!reset":
					chat = []
					irc.send("PRIVMSG", target, "Context has been reset")
				case "!quote" if len(params) > 0:
					print(irc.quote(" ".join(params)))
				case _:
					irc.send("PRIVMSG", target, "Unknown command or wrong params!")
			return

		chat.append({
			"role":"user",
			"content":"<"+user+"> "+msg,
		})
		response=ollama.chat(model=model,messages=chat)
		chat.append({
			"role": "assistant",
			"content": response.message.content
		})

		for part in textwrap.wrap(response.message.content, 235):
			irc.send("PRIVMSG", target, part)


print("Ircaifu: Connected. Type IRC quotes here. /quit to disconnect.")

while True:
	user_input = input("> ")
	if user_input.lower() == "/quit":
		print("Disconnecting")
		irc.disconnect()
		break
	if user_input.strip():
		irc.quote(user_input)
