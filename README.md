# Demo Telegram Automation Tool

## Features
- SideFans: Daily check in, rewards tasks, pass
- MoonBix: Daily check in, Play game
- Blum: Daily check in, farming, earn
- HamsterKombat: Earn (Daily), Background (Buy new cards and upgrade cards)

## Prerequisites
- Python 3.9+
- Android Device (Android 5.0 or higher)

## Installation linux
1. Installed python and git.
   
   Suggestion: Use python version 3.10+

   python
   ```shell
   sudo apt install python3 python3-pip
   ```
   git
   ```shell
   sudo apt install git
   ```

2. Clone this repository
   
   ```shell
   git clone https://github.com/baby-hero/demo_auto_tele_app.git
   ```

3. Goto demo_auto_tele_app directory

   ```shell
   cd demo_auto_tele_app
   ```

4. Install virtual environment and the require libraries
   
    ```bash
    make venv
    source tele_venv/bin/activate
    ```

5. Rename file `.env.example` to `.env`
    - Update `ADB_HOST` and `ADB_PORT`
    - Fill in your Telegram Bot Token and Channel ID if you want to use it.

6. Run 
    ```bash
    source tele_venv/bin/activate
    python src/main.py
    ```
    OR
    ```bash
    sh run.sh
    ```
