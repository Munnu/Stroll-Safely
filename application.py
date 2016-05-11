from flask import Flask, render_template, url_for
app = Flask(__name__)

# at somep point our routes will be .jsons

@app.route('/')
def index():
    """ runs app name mainspace """
    return render_template("main.html")

if __name__ == '__main__':
    app.run(debug=True)
