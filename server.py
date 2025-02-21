from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import PyPDF2
from groq import Groq
import paypalrestsdk

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configurar PayPal
paypalrestsdk.configure({
    "mode": "sandbox",  # Cambia a "live" para producción
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})

# Función para generar respuesta con Groq
def generate_response(prompt, max_tokens=300):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama3-13b",
        messages=[
            {"role": "system", "content": "Eres un experto en recursos humanos."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response.choices[0].message.content

# Endpoint para análisis básico
@app.route("/analyze-basic", methods=["POST"])
def analyze_basic():
    data = request.json
    cv_text = data["cv"]
    job_description = data["job_description"]

    prompt = f"CV: {cv_text}\nDescripción del empleo: {job_description}\nProporciona 2 razones claras y concisas por las que esta persona podría no ser contratada."
    analysis = generate_response(prompt, max_tokens=100)

    return jsonify({"analysis": analysis})

# Endpoint para crear un enlace de pago
@app.route("/create-payment", methods=["POST"])
def create_payment():
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "transactions": [{
            "amount": {"total": "10.00", "currency": "USD"},
            "description": "Acceso Premium al Análisis de CV"}],
        "redirect_urls": {
            "return_url": "https://tu-sitio-web.com/success",  # URL de éxito
            "cancel_url": "https://tu-sitio-web.com/cancel"     # URL de cancelación
        }
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return jsonify({"approval_url": link.href})
    return jsonify({"error": "Error al crear el enlace de pago"}), 500

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8000)))