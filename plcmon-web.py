from flask import Flask, render_template

import config

app = Flask(__name__)


@app.route('/')
def plcmon_status():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
