from flask import Flask, request, jsonify, render_template
import wikipedia

app = Flask(__name__)

# Define the normalize_query function
def normalize_query(query):
    """
    Normalize the user query to improve the chances of finding a Wikipedia page.
    - Strips extra spaces.
    - Capitalizes each word (to match Wikipedia's title format).
    """
    return query.strip().title()  # Capitalize each word

# Function to query Wikipedia for a summary of the input message
def query_local_model(message):
    """
    Query Wikipedia for a summary of the input message.
    """
    try:
        print(f"Original query: {message}")  # Debugging
        normalized_message = normalize_query(message)
        print(f"Normalized query: {normalized_message}")  # Debugging

        # Attempt to fetch the summary
        summary = wikipedia.summary(normalized_message, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        # Provide disambiguation options
        options = e.options[:5]  # Limit to 5 suggestions
        return f"Your query is ambiguous. Did you mean: {', '.join(options)}?"
    except wikipedia.exceptions.PageError:
        # Suggest refining the query
        return "Sorry, I couldn't find a page on that topic. Please try refining your query."
    except wikipedia.exceptions.HTTPTimeoutError:
        return "The request timed out. Please try again later."
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'response': 'Please enter a message.'}), 400

    if len(user_message) > 500:
        return jsonify({'response': 'Message too long. Keep it under 500 characters.'}), 400

    response = query_local_model(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
