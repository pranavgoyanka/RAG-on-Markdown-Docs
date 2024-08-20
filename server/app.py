from flask import Flask, render_template, request, jsonify
import os
from model.build_model import rag

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads/"

llm: rag = None

# Initialize RAG state
rag_enabled = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        global llm 
        llm = rag(file_path, "./db")
        return (
            jsonify(
                {
                    "message": "File uploaded successfully!",
                    "file_path": file_path,
                }
            ),
            200,
        )


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    # Here you would handle the chat logic. For this example, we'll echo the message back.
    global llm
    global rag_enabled
    if (llm and llm.isInitialised()):
      response_message = llm.get_llm_response(user_message, enableRAG=rag_enabled)
    else:
      response_message = "Error, LLM not initialised!" + "rag_enabled " + str(rag_enabled)
    return jsonify({"response": response_message, "using_rag": rag_enabled})

@app.route('/toggle_rag', methods=['POST'])
def toggle_rag():
    global rag_enabled
    rag_enabled = not rag_enabled
    print({"rag_enabled": rag_enabled})
    return jsonify({"rag_enabled": rag_enabled})

@app.route('/get_rag_status', methods=['GET'])
def get_rag_status():
    global rag_enabled
    return jsonify({"rag_enabled": rag_enabled})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
