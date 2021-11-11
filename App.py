from flask import Flask
import os

app = Flask(__name__)
app.secret_key = os.urandom(34)


@app.route('/')
def index():
    return "Hola Tierra"


def main():
    if __name__ == "__main__":
        app.run(debug=True)


main()
