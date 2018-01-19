from flask import Flask, render_template
from flask_script import Manager, Server

app = Flask(__name__)

manager = Manager(app)

manager.add_command('server', Server())


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


if __name__ == '__main__':
    manager.run()
