# fe_app/ai.py

from flask import Blueprint, request, jsonify, current_app
import google.generativeai as genai

print("\n--- Modelos Disponibles (Desde ai.py) ---")
try:
 
    print("Nota: Listando modelos de IA dentro de la ruta /send_message al configurarse.")
    pass 

except Exception as e:
    print(f"Error al intentar listar modelos (puede que la clave aún no esté configurada): {e}")
print("--------------------------------------\n")

persona_prompts = {
    'agustin_hipona': """Eres un asistente de IA que debe responder como Agustín de Hipona...""", 
    'tomas_aquino': """Eres un asistente de IA que debe responder como Santo Tomás de Aquino...""",   
    'martin_lutero': """Eres un asistente de IA que debe responder como Martín Lutero...""",  
    'papa_francisco': """Eres un asistente de IA que debe responder como el Papa Francisco...""", 
    'elena_g_white': """Eres un asistente de IA que debe responder como Elena G. de White..."""
}


ai_bp = Blueprint('ai_bp', __name__)

@ai_bp.route('/send_message', methods=['POST'])
def receive_message():
    data = request.get_json()
    if not data or 'message' not in data or 'character' not in data:
        return jsonify({"status": "error", "message": "Datos JSON inválidos o incompletos"}), 400

    user_message = data.get('message')
    character_id = data.get('character')
    conversation_history = data.get('history', [])

    print(f"Mensaje recibido: {user_message} (Personaje: {character_id})")
    print(f"Historial recibido (últimos {min(len(conversation_history), 5)} mensajes): {conversation_history[-min(len(conversation_history), 5):]}")

    ai_response = "Error al generar respuesta de la IA."

    try:
        google_ai_api_key = current_app.config.get('GOOGLE_AI_API_KEY')
        if not google_ai_api_key:
             print("Error: Clave de API de Google AI no encontrada en la configuración.")
             return jsonify({"status": "error", "message": "Clave de API de Google AI no configurada en el servidor."}), 500
        genai.configure(api_key=google_ai_api_key)

        model = genai.GenerativeModel('gemini-1.5-pro')

        prompt_instruction = persona_prompts.get(character_id, """Eres un asistente de IA experto en teología y filosofía cristiana, responde de forma clara y útil sobre temas bíblicos y de fe. No te presentes, solo responde.""")
        if character_id not in persona_prompts:
            print(f"Advertencia: No se encontró prompt específico para el personaje ID: {character_id}. Usando prompt por defecto.")

        initial_chat_history = [
            {"role": "user", "parts": [{"text": prompt_instruction}]},
            {"role": "model", "parts": [{"text": "Entendido. Procederé a responder como la personalidad asignada."}]}
        ]
        if conversation_history and conversation_history[-1].get('role') == 'user' and conversation_history[-1].get('parts') and conversation_history[-1]['parts'][0].get('text') == user_message:
             initial_chat_history.extend(conversation_history[:-1])
        else:
             initial_chat_history.extend(conversation_history)


        chat = model.start_chat(history=initial_chat_history)
        response = chat.send_message(user_message, request_options={'timeout': 60})

        if hasattr(response, 'text') and response.text:
            ai_response = response.text
        else:
            print("La IA no generó texto o la respuesta fue bloqueada.")
            feedback = getattr(response, 'prompt_feedback', 'No feedback disponible')
            candidates = getattr(response, 'candidates', 'No candidates disponibles')
            print(f"Prompt Feedback: {feedback}")
            print(f"Candidates: {candidates}")
            ai_response = "No pude generar una respuesta para eso. La respuesta pudo ser bloqueada por seguridad o no entendí la pregunta. Por favor, intenta con otra pregunta o reformula la actual."

    except Exception as e:
        print(f"Error al llamar a la API de Google AI: {e}")
        ai_response = f"Error al comunicarse con la API de IA: {e}"

    return jsonify({
        "status": "success",
        "user_message": user_message,
        "character": character_id,
        "ai_response": ai_response
    })