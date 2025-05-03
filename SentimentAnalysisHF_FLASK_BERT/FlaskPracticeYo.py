from flask import Flask, render_template
from flask_socketio import SocketIO, send
from pydantic import BaseModel, validator, ValidationError
from transformers import pipeline

classifier = pipeline("sentiment-analysis")
print(classifier("yo"))

app = Flask(__name__)
socketio = SocketIO(app)

class Messagehandler(BaseModel):
    message: str
    @validator('message')
    def no_hash_symbol(cls, v):
        if '#' in v:
            raise ValueError("message cannot contain #")
        return v

@app.route("/")
def Homemessage():
    return render_template('home.html')

@socketio.on('message')
def handle_message(msg):
    try: 
        validated = Messagehandler(message=msg)
        # return the list of sentiment results
        sentiment = classifier(validated.message)[0]
        print("Recieved:", validated.message)
        print(f"Sentiment Score: {sentiment['label']} ({sentiment['score']:.2f})")
        response = {"message": validated.message,
                    "sentiment": sentiment['label'],
                    "score": f"{sentiment['score']:.2f}"}

        send(response, broadcast=True)
    except ValidationError as e:
        print("validation failed", e)
        send("Invalid Message: '#' is not allowed", broadcast=False)

if __name__ == '__main__':
    socketio.run(app, debug=True)