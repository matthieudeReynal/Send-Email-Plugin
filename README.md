# Send-Email-Plugin
Plugin for c-lightning

This plugin allows to send email when you connect or disconnect from a peer.

To use it you have to create a first .txt file myaddress.txt in .lightning/testnet folder if you want to use it on testnet. This .txt should be like MyNAME MyEMAIL, where you replace those two by their values.

You also have to create another .txt : message.txt which will be template of the email sent to you, in the same folder. Just copy paste:


Hi ${PERSON_NAME}

You are successfully ${STATE} with ${PEER_ADDRESS}

You will also have to make plugin executable : chmod a+x sendmail.py

Then to run plugin : ./lightning-cli sendmail --testnet

In another terminal you can connect or disconnect from a peer and notifications will be sent to you by email.
