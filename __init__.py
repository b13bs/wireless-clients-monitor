#!/usr/bin/env python3

# TODO add database support for token management instead of text file
from flask import Flask
from flask import request
from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for
from concurrent.futures import ThreadPoolExecutor
import psutil
import os
import stat
import token_management
import process_utilities
import config

app = Flask(__name__)
app.secret_key = config.flask_secret_key


def files_initialization():
    # token file
    token_management.check_token_file_existence()

    # process file
    process_file = os.path.join(config.process_path, config.process_name)
    st = os.stat(process_file)
    os.chmod(process_file, st.st_mode | stat.S_IEXEC)
    #os.chmod(process_file, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def token_validation(token):
    if token is None:
        flash("Access denied, no token supplied", "alert-danger")
        return False
    elif not token_management.token_is_good_format(token):
        flash("Access denied, bad token format", "alert-danger")
        return False
    else:
        token_status = token_management.token_check(token)
        if token_status == "expired":
            flash("Expired token", "alert-danger")
            return False
        elif token_status == "invalid":
            flash("Bad token", "alert-danger")
            return False
        elif token_status == "valid":
            #flash("Access granted", "alert-success")
            return True


@app.route("/")
def status_page():
    token = request.args.get('token')
    return_value = token_validation(token)

    if return_value:
        p = psutil.Process(process_pid)
        if p.status() == "stopped":
            flash("Scan is sleeping. SHHH, don't wake him up!!", "alert-warning")
        else:
            flash("Scan is currently running", "alert-info")
        return render_template("page.html", token=token)

    return render_template("page.html")


@app.route("/snooze")
def snooze():
    # token parameter
    token = request.args.get('token')
    token_is_valid = token_validation(token)

    # duration parameter
    duration = request.args.get('duration')
    if duration is None:
        duration = "3600"

    app.logger.debug("Snoozing!")
    if token_is_valid:
        try:
            future
        except NameError:
            pass
        else:
            if future.running():
                value = future.cancel()

        global future
        future = executor.submit(process_utilities.pause_process, process_pid, duration)
        flash("Snoozed", "alert-info")

    return redirect(url_for("status_page", token=token))


@app.route("/unsnooze")
def unsnooze():
    # token parameter
    token = request.args.get('token')
    token_is_valid = token_validation(token)

    if token_is_valid:
        app.logger.debug("Unsnoozing!")
        process_utilities.resume_process(process_pid)

    return redirect(url_for("status_page", token=token))


if __name__ == "__main__":
    # http://stackoverflow.com/questions/22615475/flask-application-with-background-threads
    executor = ThreadPoolExecutor(5)
    process_pid = process_utilities.start_process()


    app.logger.debug("Scan started. PID=%s" % process_pid)
    app.config['DEBUG'] = False
    app.run(host="0.0.0.0", use_reloader=False)
