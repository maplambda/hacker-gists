import os

from flask import Flask, render_template, redirect, url_for

import model

app = Flask(__name__)

@app.context_processor
def mixpanel_token():
    return dict(mixpanel_token=os.getenv('MIXPANEL_TOKEN'),
                prod_mixpanel_token='674338aad6c56609fcffc10c2dbf6d5')

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

