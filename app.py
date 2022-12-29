import sqlite3
from flask import Flask, request, jsonify
import openai
import os

# Set up the OpenAI API client
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__, static_folder="static")

@app.route("/", methods=["GET"])
def index():
    return app.send_static_file("index.html")


@app.route('/chat', methods=['POST'])
def chat():
    # Connect to the SQLite database
    conn = sqlite3.connect("conversation_history.db")
    cursor = conn.cursor()

    # Create the table to store the conversation history, if it doesn't already exist
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS conversation_history (id INTEGER PRIMARY KEY, message TEXT)"
    )
    conn.commit()

    # Get the user's message from the request
    user_message = request.json['message']

    # Retrieve the conversation history from the database
    cursor.execute("SELECT message FROM conversation_history")
    conversation_history = "\n".join([row[0] for row in cursor.fetchall()])

    # Use the GPT-3 API to generate a response, using the conversation history as context
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"{conversation_history}\n{user_message}",
        #prompt=user_message,
        max_tokens=1024,
        temperature=0.5
    )

    # Save the user's message and the response to the database
    cursor.execute("INSERT INTO conversation_history (message) VALUES (?)", (user_message,))
    cursor.execute("INSERT INTO conversation_history (message) VALUES (?)", (response["choices"][0]["text"],))
    conn.commit()

    # Close the connection to the database
    conn.close()

    # Return the response as JSON
    return jsonify({"response": response["choices"][0]["text"]})