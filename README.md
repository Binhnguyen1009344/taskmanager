# Task Manager

Ung dung quan ly cong viec ca nhan xay dung bang Flask + MySQL.

## Yeu cau
- Ubuntu Server 24.04
- Python 3.12+
- MySQL 8.0
- Nginx
- Gunicorn

## Cai dat

### 1. Clone repo
    git clone https://github.com/Binhnguyen1009344/taskmanager.git
    cd taskmanager

### 2. Tao virtual environment
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

### 3. Cau hinh .env
    cp .env.example .env
    nano .env

### 4. Tao database MySQL
    sudo mysql -u root -p
    CREATE DATABASE taskmanager;
    CREATE USER 'taskuser'@'localhost' IDENTIFIED BY 'matkhau';
    GRANT ALL ON taskmanager.* TO 'taskuser'@'localhost';
    FLUSH PRIVILEGES;

### 5. Chay ung dung
    python app.py
