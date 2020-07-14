#!/usr/bin/env python

# -*- coding: utf-8 -*-

""" 
CheerCommand for Twitch
    
    0.0.1
        Initial Release
    0.0.2
        Separated functions, improved structure
    0.0.3
        Updated to include discounts for subs
    0.0.4
        Separated auth and config
        Added functions for adding and removing users from random command list
        Added handling for messages that come in with no tags
        Added ability for users to execute random commands using channel points
    0.0.5
        Set limits on boxboss to 10 commands
    0.1.0
        Refactored trigger methods
        Added class to create trigger objects
        Added support for csv config for all triggers
    0.1.1
        Added command to check if the cheerCommand script is active
        Added command to toggle the cheer command when squad is in a top 10 situation
    0.1.2
        Added sub madness mode for all channel access to !random command
    0.1.3
        Added !wasd mode to mix up wasd
        Added handling for multiple config files
    0.1.4
        Fixed !wasd duration
    0.2.0

        Reworked command, action, and configuration

http://twitch.tv/johnlonnie

"""

"""
TODO:
    Move global vars into singletons
    Move keyboard/mouse commands away from exec utilization (currently a limit of libs' argument handling)
    Optimize IRCv3 tag parses in utility
"""

#--------------------------------
# SCRIPT IMPORT LIBRARIES
#--------------------------------

import auth
import utility
import cfg
import socket
import cmds

#--------------------------------
#GLOBAR VARS
#--------------------------------

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
scriptActive = 0 #toggle for whether chat has access to cheer commands or not
subMode = 0 #toggle for special mode that gives all chat access to boxBoss special perms
randomAccess = [] #list of specific chat users who are granted access to special perms
boxBoss = "" #username in the channel that receives special permissions
boxBossCredits = 10 #number of times the boxboss can use their special commands
commandCounter = 0

#--------------------------------
#HELPERS
#--------------------------------

#send to the socket
def send(s, text):
    s.send(text.encode('utf-8') + b'\r\n')

#send chat message
def chat(sock, msg):

    #Send a chat message to the server.
    #Keyword arguments:
    #sock -- the socket over which to send the message
    #msg  -- the message to be sent

    sock.send(("PRIVMSG {} :{}\r\n".format(auth.CHAN, msg)).encode("UTF-8"))


def trigger(bits: int, discount: bool = False):
    cmd = cmds.run(bits, discount=discount)
    if cmd is not None:
        send(s, cmd.message)


def trigger_random():
    cmd = cmds.run_random()
    send(s, cmd.message)


def wacky_wasd():
    cmd = cmds.run('wackywasd')
    send(s, cmd.message)


def randomPermit(twitchUser): #add user to random command permission list
    global randomAccess
    global s
    if twitchUser in randomAccess:
        chat(s, twitchUser + " already has access to random keyboard commands.")
        return
    else:
        randomAccess.append(twitchUser)
        chat(s, twitchUser + " has been granted access to random keyboard commands.")

def randomRevoke(twitchUser): #remove user from random command permission list
    global randomAccess
    global s
    if twitchUser in randomAccess:
        randomAccess.remove(twitchUser)
        chat(s, twitchUser + " has been removed from random keyboard commands.")
    else:
        chat(s, twitchUser + " doesn't have access to random keyboard commands.")
        return

def bossChange(twitchUser): #changes the box boss
    global boxBoss
    global boxBossCredits
    global s
    boxBoss = twitchUser
    chat(s, twitchUser + " Is now the BoxBoss and has access to the !random command when the bits overlay is active")
    boxBossCredits = 10

def gameChange(newgame): #changes game for cheerbot
    global currentgame
    global s
    currentgame = newgame
    chat(s, "I have updated the game to " + currentgame)

def cheerToggle():
    global scriptActive
    print("Toggling the cheer command status")
    if scriptActive == 0:
        scriptActive = 1
        scriptStatusMessage = "activated!"
        print(scriptActive)
    else:
        scriptActive = 0
        scriptStatusMessage = "stopped!"
        print(scriptActive)
    chat(s, "CheerCommand has been " + scriptStatusMessage)

def subModeToggle():
    global subMode
    global scriptActive
    print("Toggling sub mode")
    if subMode == 0:
        subMode = 1
        subStatusMessage = "activated!"
        if scriptActive == 0:
            cheerToggle()
        print(subMode)
    else:
        subMode = 0
        subStatusMessage = "stopped!"
        if scriptActive == 1:
            cheerToggle()
        print(subMode)
    chat(s, "Sub Goal Madness has been " + subStatusMessage)


#--------------------------------
# MAIN LOOP
#--------------------------------

def bot_loop():

    global scriptActive
    global subMode
    global randomAccess
    global boxBossCredits
    global commandCounter
    global s

    #connect to the IRC chat
    s.connect((auth.HOST, auth.PORT))
    s.send("PASS {}\r\n".format(auth.PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(auth.NICK).encode("utf-8"))
    s.send("JOIN {}\r\n".format(auth.CHAN).encode("utf-8"))
    s.send("CAP REQ :twitch.tv/tags".encode("utf-8") + b'\r\n')

    chat(s, "I have arrived")

    while True:
        data = s.recv(1024)
        if data.decode("utf-8") == "PING :tmi.twitch.tv\r\n":
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            print("DATA")
            print (data)

            data = data.decode() # turn socket message into byte type
            print("DATA DECODED")
            print (data)

            parsedMessage = utility.ircv3_message_parser(data) # run message through decoder to get list with tags

            print("PARSED MESSAGE")
            print(parsedMessage)

            tagStrip = parsedMessage[2] # separate tag dict from list
            print("TAG STRIPPED")

            # get the username
            if 'display-name' in tagStrip:
                username = tagStrip.get('display-name').strip()

            # get the message from the parser and remove unnecessary chars 
            separatedMessage = parsedMessage[3]
            print("MESSAGE STRIPPED")
            try:
                isolatedMessage = separatedMessage[1]
                print("MESSAGE ISOLATION COMPLETE")
            except IndexError:
                isolatedMessage = ""
                print("MESSAGE ISOLATED EXCEPTION")
            if len(isolatedMessage) > 0:
                trueMessage = isolatedMessage[1:] # separate message from username who sent it
                print("TRUE MESSAGE COMPLETE")
                cleanMessage = trueMessage.strip() # clean the message by stripping leading and trailing chars
                print("MESSAGE CLEANED")
                splitMessage = trueMessage.split(' ') # split the message into a list
                print("MESSAGE SPLIT")


            if "badges" in tagStrip: # look for badges in message
                print("BADGER DETECTED")
                userBadges = tagStrip.get('badges')

                # MOD COMMANDS
                if userBadges == True: # handle users chatting without tags
                    print ("CONTINUING")
                    continue

                if "moderator" in userBadges or "broadcaster" in userBadges:
                    print("MOD OR BROADCASTER COMMAND")
                    if cleanMessage == "!cheercommand":
                        print("cheercommand detected")
                        cheerToggle()

                    if cleanMessage == "!submadness":
                        print("SUB MADNESS INITIATED")
                        subModeToggle()

                    if cleanMessage == "!cheercheck":
                        if scriptActive == 0:
                            chat(s, "Cheer Command is currently OFF")
                        else:
                            chat(s, "Cheer Command is currently ON")

                    if splitMessage[0] == "!addrandom" and len(splitMessage) == 2:
                        print("ADDRANDOM DETECTED")
                        randomPermit(splitMessage[1].strip().lower())

                    if splitMessage[0] == "!removerandom" and len(splitMessage) == 2:
                        randomRevoke(splitMessage[1].strip().lower())
                        print("REMOVERANDOM DETECTED")

                    if cleanMessage == "!randomlist":
                        if len(randomAccess) > 0:
                            currentAccessList = ', '.join(randomAccess)
                            chat(s, currentAccessList)
                        else:
                            chat(s, "The random access list is empty.")

                    if splitMessage[0] == "!bossupdate" and len(splitMessage) == 2:
                        print("BOSSCHANGE")
                        bossChange(splitMessage[1].strip().lower())
                
                if "broadcaster" in userBadges:
                    if splitMessage[0] == "!test" and len(splitMessage) == 2:
                        try:
                            commandNumber = int(splitMessage[1])
                        except:
                            print("SORRY I CAN'T CONVERT THAT TO AN INT")
                        else:
                            cmd = cmds.get_nth(commandNumber)
                            if cmd is not None:
                                trigger(cmd.cost)
                    if cleanMessage == "!wasdtest":
                        wacky_wasd()

            if scriptActive == 1:           
                if cleanMessage == "!random":
                    print("RANDOM DETECTED")
                    if subMode == 1:
                        trigger_random()
                        print("!RANDOM COMMAND VIA SUBMODE DETECTED")
                    elif username.strip().lower() == boxBoss.lower():
                        print("PERMISSION DETECTED")
                        if boxBossCredits > 0:
                            trigger_random()
                            print("!RANDOM COMMAND VIA BOXBOSS TRIGGERED")
                            boxBossCredits = boxBossCredits - 1
                            chat (s, "You have " + str(boxBossCredits) + " random commands remaining.")
                        else:
                            chat (s, "Sorry, boss. You don't have any random credits left")
                    elif username.strip().lower() in randomAccess:
                        trigger_random()
                        print("!RANDOM COMMAND VIA RANDOMACCESS DETECTED")

                if cleanMessage == "!wasd":
                    if username.strip().lower() == boxBoss.lower():
                        print("WASD PERMISSION DETECTED")
                        if boxBossCredits > 0:
                            print("trying WASD")
                            wacky_wasd()
                            boxBossCredits = boxBossCredits - 1
                            chat (s, "You have " + str(boxBossCredits) + " random commands remaining.")

                if "custom-reward-id" in tagStrip:
                    if tagStrip.get('custom-reward-id') == cfg.channelPoint1:
                        trigger_random()


                if "bits" in tagStrip:
                    cheerAmount = int(tagStrip.get('bits'))      # get bit amount value
                    commandCounter = commandCounter + 1 # update the total number of cheer commands

                    if "subscriber" in userBadges or "founder" in userBadges: # check that 'bits' is in the dict as key and the cheerer is a subscriber
                        print(f"SUB Bits: {cheerAmount}")

                        trigger(cheerAmount, discount=True)

                    else:
                        print(f"Bits: {cheerAmount}")

                        trigger(cheerAmount)

                    if commandCounter == 10:
                        boxBossCredits = boxBossCredits + 1
                        chat (s, "Ooh that cheer gave our BoxBoss an extra credit. They now have " + str(boxBossCredits))
                        commandCounter = 0

                if cleanMessage == "!top10":
                    cheerToggle()
                    chat(s, "We've turned off cheer command because we're in a top 10 situation.")


    sleep(1)
if __name__ == "__main__":
    bot_loop()