from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', '127.0.0.1')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('tasks'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            flash('Ten dang nhap da ton tai!', 'danger')
        else:
            hashed = generate_password_hash(password)
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
            mysql.connection.commit()
            flash('Dang ky thanh cong!', 'success')
            return redirect(url_for('login'))
        cur.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('tasks'))
        flash('Sai ten dang nhap hoac mat khau!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/tasks')
@login_required
def tasks():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
    task_list = cur.fetchall()
    cur.close()
    return render_template('tasks.html', tasks=task_list)

@app.route('/tasks/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        if not title:
            flash('Tieu de khong duoc de trong!', 'danger')
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tasks (user_id, title, description, priority) VALUES (%s, %s, %s, %s)", (session['user_id'], title, description, priority))
            mysql.connection.commit()
            cur.close()
            flash('Them cong viec thanh cong!', 'success')
            return redirect(url_for('tasks'))
    return render_template('add_task.html')

@app.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s AND user_id = %s", (task_id, session['user_id']))
    task = cur.fetchone()
    if not task:
        return redirect(url_for('tasks'))
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        status = request.form.get('status', 'pending')
        cur.execute("UPDATE tasks SET title=%s, description=%s, priority=%s, status=%s WHERE id=%s AND user_id=%s", (title, description, priority, status, task_id, session['user_id']))
        mysql.connection.commit()
        cur.close()
        flash('Cap nhat thanh cong!', 'success')
        return redirect(url_for('tasks'))
    cur.close()
    return render_template('edit_task.html', task=task)

@app.route('/tasks/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (task_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    flash('Da xoa cong viec!', 'success')
    return redirect(url_for('tasks'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
