#!/usr/bin/env python3

import csv
from os.path import join
import os
from lightning import Plugin, LightningRpc
import pandas as pd
import numpy as np
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from string import Template

# I know it's really ugly ^^
MY_ADDRESS = "ilove.lightning@outlook.com"
PASSWORD = "Lightning<3"

def get_contacts(filename):
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            name=a_contact.split()[0]
            email=a_contact.split()[1]
    return name, email


def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
       template_file_content = template_file.read()
    return Template(template_file_content)

# set up the SMTP server
s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
s.starttls()
s.login(MY_ADDRESS, PASSWORD)

def sendMessage(state, peer_address):
    print(os.path.abspath(os.getcwd()))
    name, email = get_contacts('myaddress.txt')  # read address
    message_template = read_template('message.txt')
    msg = MIMEMultipart()    

    # add in the actual person name to the message template
    message = message_template.substitute(PERSON_NAME=name.title(), STATE=state, PEER_ADDRESS=peer_address)
    
    # setup the parameters of the message
    msg['From']=MY_ADDRESS
    msg['To']=email
    msg['Subject']="Succesful connection/deconnection to a peer"
    # add in the message body
    msg.attach(MIMEText(message, 'plain'))

    # send the message via the server set up earlier.
    s.send_message(msg)
    del msg


plugin = Plugin()
@plugin.method("sendmail")


def hello(plugin):
    """Send email when you connect or disconnect from a peer
    """
    
    peers = plugin.rpc.listpeers()["peers"]
    tmp = [0, 0, 0, 0]
    try:
        i = 0
        while True :
            infos = plugin.rpc.getinfo()
            row = []                  
            # we can read many features and send email for more than just connection to peers
            num_peers = infos["num_peers"]
            num_pending_channels = infos["num_pending_channels"]
            num_active_channels = infos["num_active_channels"]
            num_inactive_channels = infos["num_inactive_channels"]
            row.append(num_peers)
            row.append(num_pending_channels)
            row.append(num_active_channels)
            row.append(num_inactive_channels)
            if i == 0 : tmp = row
            if num_peers > tmp[0] and i > 0:
                lastPeer = plugin.rpc.listpeers()["peers"][-1]
                lastPeerId = lastPeer["id"]
                print("You are succesfully connected to a new peer : ", lastPeerId)
                peers = plugin.rpc.listpeers()["peers"]
                sendMessage("connected", lastPeerId)
                tmp = row
            if num_peers < tmp[0] and i > 0:
                #print("i = ", i)
                peersid = []
                newpeersid = []
                deletedPeer = ""
                for peer in peers:
                    peersid.append(peer["id"])
                newpeers = plugin.rpc.listpeers()["peers"]
                for peer in newpeers:
                    newpeersid.append(peer["id"])
                #print(newpeers)
                for peer in peersid :
                    if peer not in newpeersid :
                        #print("in if")
                        deletedPeer = peer
                    
                peers = newpeers
                print("you are succesully disconnected from : ", deletedPeer)
                sendMessage("disconnected", deletedPeer)
                tmp = row
            
            i = i + 1
            #return (num peers = num_peers)

    except Exception as error:
        print(error)
        return "Export failed: " + str(error)

@plugin.init()
def init(options, configuration, plugin):
    global rpc_interface
    # connect to the rpc interface
    rpc_interface = LightningRpc(join(configuration['lightning-dir'], configuration['rpc-file']))
    plugin.log("Plugin sendmail.py initialized")


plugin.run()