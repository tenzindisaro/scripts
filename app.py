from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def iniciar_jogo():
    os.system("python main.py")
    return "Jogo iniciado localmente via Flask."

if __name__ == "__main__":
    app.run(debug=True)

