from flask import Flask, render_template, url_for
from model import Crime_Data_NYC, connect_to_db

app = Flask(__name__)

# at somep point our routes will be .jsons

@app.route('/')
def index():
    """ runs app name mainspace """
    return render_template("main.html")

if __name__ == '__main__':
    app.run(debug=True)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    connect_to_db(app)
    app.run()
