from openai import OpenAI  # type: ignore
from flask import Flask, send_from_directory, request, jsonify, Response, render_template_string, redirect, url_for, session  # type: ignore
import re

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Requerido para sesiones

# Credenciales ficticias
USUARIO_VALIDO = "admin"
CONTRASEÑA_VALIDA = "1234"

client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama',  # required, but unused
)

# Vista de login
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        contraseña = request.form["contraseña"]
        if usuario == USUARIO_VALIDO and contraseña == CONTRASEÑA_VALIDA:
            session['usuario'] = usuario
            return redirect(url_for('serve_index'))
        else:
            return "💔 Credenciales inválidas. Intenta otra vez."
    return render_template_string('''
        <h2>Inicio de Sesión</h2>
        <form method="post">
            Usuario: <input type="text" name="usuario"><br>
            Contraseña: <input type="password" name="contraseña"><br>
            <input type="submit" value="Ingresar">
        </form>
    ''')

# Redirigir al index.html si está logueado
@app.route('/', methods=["GET"])
def serve_index():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    return send_from_directory('dist', 'index.html')

# Servir archivos estáticos desde dist
@app.route('/<path:path>', methods=["GET"])
def serve_static(path):
    if not session.get('usuario'):
        return redirect(url_for('login'))
    return send_from_directory('dist', path)

# API para analizar riesgos
@app.route('/analizar-riesgos', methods=['POST'])
def analizar_riesgos():
    data = request.get_json()
    activo = data.get('activo')
    if not activo:
        return jsonify({"error": "El campo 'activo' es necesario"}), 400
    riesgos, impactos = obtener_riesgos(activo)
    return jsonify({"activo": activo, "riesgos": riesgos, "impactos": impactos})

# API para sugerir tratamiento
@app.route('/sugerir-tratamiento', methods=['POST'])
def sugerir_tratamiento():
    data = request.get_json()
    activo = data.get('activo')
    riesgo = data.get('riesgo')
    impacto = data.get('impacto')

    if not activo or not riesgo or not impacto:
        return jsonify({"error": "Los campos 'activo', 'riesgo' e 'impacto' son necesarios"}), 400

    entrada_tratamiento = f"{activo};{riesgo};{impacto}"
    tratamiento = obtener_tratamiento(entrada_tratamiento)

    return jsonify({
        "activo": activo,
        "riesgo": riesgo,
        "impacto": impacto,
        "tratamiento": tratamiento
    })

# Función para obtener tratamiento usando LLM
def obtener_tratamiento(riesgo):
    response = client.chat.completions.create(
        model="ramiro:instruct",
        messages=[
            {"role": "system", "content": "Responde en español, eres una herramienta para gestión de riesgos ISO 27001..."},
            {"role": "user", "content": "mi teléfono móvil;Acceso no autorizado;un atacante puede acceder..."},
            {"role": "assistant", "content": "Establecer un bloqueo de pantalla..."},
            {"role": "user", "content": riesgo}
        ]
    )
    return response.choices[0].message.content

# Función para obtener riesgos usando LLM
def obtener_riesgos(activo):
    response = client.chat.completions.create(
        model="ramiro:instruct",
        messages=[
            {"role": "system", "content": "Responde en español, eres una herramienta para gestión de riesgos ISO 27001..."},
            {"role": "user", "content": "mi raspberry pi"},
            {"role": "assistant", "content": "• **Acceso no autorizado**: ..."},
            {"role": "user", "content": activo}
        ]
    )
    answer = response.choices[0].message.content
    patron = r'\*\*\s*(.+?)\*\*:\s*(.+?)\.(?=\s*\n|\s*$)'
    resultados = re.findall(patron, answer)
    riesgos = [r[0] for r in resultados]
    impactos = [r[1] for r in resultados]
    return riesgos, impactos

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5500)
