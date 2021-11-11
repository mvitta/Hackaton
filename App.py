from flask import Flask, render_template
import os

app = Flask(__name__)
app.secret_key = os.urandom(34)


@app.route('/', methods=['POST', 'GET'])
def login():
    return render_template('login.html')


@app.route('/registro', methods=['POST', 'GET'])
def registro():
    return render_template('registro.html')


def main():
    if __name__ == "__main__":
        app.run(debug=True)


main()
