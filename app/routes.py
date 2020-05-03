from app import app
from flask import (render_template, render_template_string, request,
        session, send_from_directory, send_file)
import os, sqlite3

with open('secretkey') as keyfile:
    app.secret_key = keyfile.readline()
    keyfile.close()


@app.route('/')
def test():
    return 'test'
