<div align="center"><img src="https://raw.githubusercontent.com/MrAminiDev/Tabchi-Mokhber/main/Tabchi-Mokhber.png" width="500"></div>
<div align="center"><br>

  برای توضیحات <a href="https://github.com/MrAminiDev/Tabchi-Mokhber/blob/main/README-fa.md"> فارسی اینجا بزنید </a>

</div>
<br><br>

# 🤖 Mokhber Bot - Automated Advertisement & User Collection Bot
Mokhber is an advanced Telegram bot designed for automated advertising and user collection. It allows you to gather user IDs from groups and private chats, store them, and send targeted promotional messages efficiently. With smart scheduling, random delays, and active user detection, Mokhber ensures optimal message delivery while minimizing the risk of getting restricted by Telegram.<br>
Key Features:

✅ Automatic user collection from groups and private chats<br>
✅ Bulk messaging with smart delays and scheduling<br>
✅ Randomized bio updates for a more natural presence<br>
✅ Active user filtering to improve engagement rates<br>
✅ Multi-group message broadcasting for wider reach<br>
✅ Automated reports and delivery tracking<br>

Mokhber is ideal for businesses and individuals who want to expand their audience and maximize their reach in Telegram while maintaining security and efficiency.

# Installation instruction

1- Update the server:
```shell
sudo apt update && sudo apt upgrade -y
```

2- Install Python
```shell
sudo apt install python3 python3-pip -y
```
- Install prerequisites
```shell
pip install uv
```

4- Download the project
```shell
apt install wget unzip
mkdir -p mokhber
wget -O tabchi-mokhber.zip https://github.com/MrAminiDev/Tabchi-Mokhber/archive/refs/heads/main.zip
unzip tabchi-mokhber.zip -d mokhber
mv mokhber/Tabchi-Mokhber-main/* mokhber/
rm -r mokhber/Tabchi-Mokhber-main
rm tabchi-mokhber.zip
```

- Enter the Mokhber folder using the following command
```shell
cd mokhber
```

6- Edit the main.py file and put your token information in lines 14 and 13
```shell
nano main.py
```
To get API ID, HASH ID, go to https://my.telegram.org and create your program
In line 15, put the admin ID number that can control the bot

8- Run the following command to run the bot
```shell
uv run main.py
```
## To keep the bot running permanently, you need to use the service
```sh
nano /etc/systemd/system/mokhber.service
```
Put the following content in the service file
```service
[Unit]
Description=mokhber
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/mokhber
ExecStart=/usr/local/bin/uv run main.py
Restart=always

[Install]
WantedBy=multi-user.target
```
Activation:
```sh
sudo systemctl daemon-reload
sudo systemctl enable mokhber.service
sudo systemctl start mokhber.service
```
Shutdown the bot:
```sh
sudo systemctl stop mokhber.service
```
Viewing the bot logs:
```sh
journalctl -u mokhber.service -f
```

##  Support with Crypto 
- TRX : `TLfVhyK6ihTuPNtFpuhULNuJaiKFLHxMFL`

## Stargazers over time
[![Stargazers over time](https://starchart.cc/MrAminiDev/Tabchi-Mokhber.svg?variant=adaptive)](https://starchart.cc/MrAminiDev/Tabchi-Mokhber)
