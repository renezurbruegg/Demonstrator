# PULPETUM MOBILE

## INSTALL INSTRUCTIONS
#### Set up Raspberry pi using NOOBS

Download NOOBS and boot Raspberry Pi

[Instructions](https://www.raspberrypi.org/downloads/noobs/)

Set up the operating system using Monitor and Keyboard. 

### Enable ssh
[See](https://www.raspberrypi.org/documentation/remote-access/ssh/)

#### Connect 
Get the Ip adress of the raspberry pi. Make sure the raspberry pi is in the same network as your computer
```bash
    ifconfig
```
Connect to the raspberry pi using ssh
 ```bash
    ssh pi@<your pi IP>
```
#### Enable I2c
```bash
    sudo raspi-config
```
#### install I2C utilities
```bash
    sudo apt-get install python-smbus i2c-tools
```

#### Restart Pi
```bash
    sudo reboot
```

#### `[ Optional `] Installing rmate for remote file editing
To edit files locally on your PC you need to set up rmate. 
Otherwise all editing of the files has to be done over ssh using console line editor like nano or vim.

1. Install rmate client on raspberry pi.
    ```bash
        pip install install rmate
    ```
2. Install an editor locally to edit the files. Must support the rmate plugin.
    e.g. Install [Visual Studio Code](https://code.visualstudio.com/download), install [Rmate Plugin](https://marketplace.visualstudio.com/items?itemName=rafaelmaiolla.remote-vscode), follow instruction from the plugin (https://medium.com/@prtdomingo/editing-files-in-your-linux-virtual-machine-made-a-lot-easier-with-remote-vscode-6bb98d0639a4) and start local server. 

3. Connect back to the Raspberry pi
    ```bash
        ssh -R 52698:127.0.0.1:52698 pi@<Raspberry Pi IP>
    ```
4. To edit e file remotely enter:
    ```bash
    rmate "yourFile.py"
    ```



#### Setting up the flask Backend Server
---

1.  Clone the repo 

    ```bash
    git clone --depth 1 https://gitlab.ethz.ch/zrene/pulp-demonstrator.git
    cd pulp-demonstrator
    ```

2.  Install the backend related requirements
    ```bash
    cd Server
    cd backend
    sudo pip install -r requirements.txt
    ```
#### Setting up the Angular Frontend Server
---
1.  Install frontend related dependencies

    -   Easiest way to handle node related dependencies is to install [nvm](https://github.com/creationix/nvm)
    -   Once you have node installed, install the project's dependencies

    ```bash
    cd ..
    cd front

    # install global dependencies
    npm install typescript -g

    # install project related dependencies
    npm install

    # run server
    ng serve --host 0.0.0.0
    ```

4.  Now navigate to `http://<Your RPI IP>:4200` 
