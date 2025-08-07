from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Servidor funcionando!"

if __name__ == '__main__':
    print("Iniciando servidor...")
    app.run(debug=True, host='0.0.0.0', port=5000) 