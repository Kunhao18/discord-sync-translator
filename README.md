# Discord Channel Synchronization Translator
🤖 A codebase that helps you set up your own discord bot that can synchronize and translate the messages among channels with different specified languages.
- Integrated free translation API - [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate) and [lingua](https://github.com/pemistahl/lingua)
- Generic backend that can easily adopt to other any other API
- Easy-to-use commands to manage the channels and groups


## Set up
Clone the repo and install the dependencies:
```
pip install -r requirements.txt
```
Create file `.env` and fill your `bot token` and `channel id` (support only one channel for now):
```
BOT_TOKEN=xxx
GUILD_ID=xxx
```
Start the bot:
```
python bot.py
```
##### (Optional) Set up the LibreTranslate API
Install the [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate) according to the github repo

Start the translator API locally (default port 18888):
```
libretranslate --port 18888
```

## Commands
> channels in the same group will be synchronized
```python
/group create [group name]             # create a new group
/group delete [group name]             # delete a group and unbind all channels
/group rename [group name] [new name]  # rename the group
/group check                           # check channel bound information of all the groups
/channel bind [channel] [group name]   # bind channel to a group, a language selection window will pop-up
/channel unbind [channel]              # unbind a channel
/channel change [channel] [new group]  # change the channel's group or language
```