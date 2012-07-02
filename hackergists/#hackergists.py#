from flask import Flask, render_template, redirect, url_for
import model

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('latest'))

@app.route('/latest')
def latest():
    gists = model.recent_gists(0)
    return render_template('index.html', params=gists, start=0)

@app.route('/latest/<int:start>')
def more(start):
    gists = model.recent_gists(start)
    return render_template('index.html', params=gists, start=start)

@app.route('/info')
def info():
    info = model.info()
    return render_template('info.html', info=info)

if __name__ == '__main__':
    app.run(debug=True)
