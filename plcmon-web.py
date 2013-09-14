import sqlite3
import datetime
from babel.dates import format_timedelta

from flask import Flask, render_template, g, redirect, url_for

import config


app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'de'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(config.DB_PATH,
                                           detect_types=sqlite3.PARSE_DECLTYPES |
                                                        sqlite3.PARSE_COLNAMES)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/plcmon')
def plcmon_status():
    last_events = get_db().execute("SELECT timestamp, app_name, app_label, event_source, "
                                   " event_text, priority FROM events ORDER BY timestamp DESC LIMIT 20"
                                   "  ").fetchall()

    try:
        is_open = get_db().execute("SELECT plcmon_data FROM events "
                                   "WHERE plcmon_data IN (1, 2) ORDER BY "
                                   "timestamp DESC LIMIT 1").fetchone()[0] == 2
    except TypeError:
        is_open = False

    try:
        is_alarm = get_db().execute("SELECT plcmon_data FROM events "
                                    "WHERE plcmon_data IN (3, 4) ORDER BY "
                                    "timestamp DESC LIMIT 1").fetchone()[0] == 3

    except TypeError:
        is_alarm = False

    try:
        last_change = get_db().execute("SELECT datetime(timestamp, 'localtime') AS '[timestamp]' FROM "
                                       "events WHERE plcmon_data IN (1, 2, 4) "
                                       "ORDER BY timestamp DESC LIMIT 1").fetchone()[0]

    except TypeError:
        last_change = "N/A"

    delta = format_timedelta(datetime.datetime.now() - last_change)

    return render_template("status.html",
                           events=last_events,
                           status=is_open,
                           alarm=is_alarm,
                           last_change=delta
    )


@app.route('/')
def index():
    return redirect(url_for('plcmon_status'))


if __name__ == '__main__':
    app.debug = False
    app.run(host="0.0.0.0", threaded=True, port=2993)
