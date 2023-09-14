from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
import os
import urllib
from utils import utilities
from random import randint
   
from speaker_verification.speechbrain.pretrained import SpeakerRecognition
verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")

app = Flask("app")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/logout", methods=['POST'])
def logout():
    if request.method == 'POST':
        if "username" in session:
            session.pop('username')
            session.pop('evaluation_data')
            return 'OK'
    return 'INVALID'

@app.route('/evaluation')
def evaluation():
    if not session.get("username"):
        session['alert_message'] = True
        return redirect(url_for("login"))
    
    current_page = 'evaluation.html'
    return render_template(current_page, current_page=current_page, data=session["evaluation_data"])

@app.route('/auth_login', methods=['POST'])
def auth_login():
    if request.method == 'POST':
        response = "True"
        photo = request.form['photo']
        number = session.get("number")
        voice = request.form['voice']
        voice += "=" * (len(voice)%4)

        app.logger.info(f'number {number}')

        dir_name = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        dir_path = f'temporary/{dir_name}'
        os.mkdir(dir_path)
        image_path = f'{dir_path}/photo.jpg'

        status = utilities.recognize_faces(photo, image_path)

        if status is None and number is not None:
            status, check_number_in_photo_results = utilities.check_number_in_photo(image_path, number, dir_path)
            
            if status is not None:
                response = status
            else:
                identify_identity, identify_face_results = utilities.identify_face(image_path, dir_path)

                if identify_identity is None:
                    response = "You have not been identified as an enrolled person, please try again!"
                else:
                    with urllib.request.urlopen(voice) as resp_:
                        data = resp_.read()

                        with open("speaker_verification/input/temp.wav", "wb") as file:
                            file.write(data)

                    username = identify_identity.lower().replace(" ", "_")

                    score, prediction = verification.verify_files("speaker_verification/input/" + username + ".wav", "speaker_verification/input/temp.wav")
                    verified = prediction[0].item()

                    if verified:
                        session['username'] = identify_identity
                        session['evaluation_data'] = f'\nOCR extracting text\n\n{check_number_in_photo_results}'
                        session['evaluation_data'] += f'\n\nFace recognition evaluation - Accepted euclidean distance <= 0.47\n\n{identify_face_results}'
                        session['evaluation_data'] += '\n\nSpeaker verification evaluation - Accepted cousine distance >= 0.25\n\n{\n\t"score": ' + str(score[0].item()) + ',\n\t"accept": ' + str(prediction[0].item()).lower() + '\n}\n'
                    else:
                        response = "Speaker not identified, please try again!!"

        else:
            response = status

    return response

@app.route('/check_photo', methods=['POST'])
def check_photo():
    if request.method == 'POST':
        response = "True"
        photo = request.form['photo']
        status = utilities.recognize_faces(photo)
        if status is not None:
            response = status

    return response

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        response_message = "You are alredy enrolled!"

        first_name = "_".join(request.form['first_name'].strip().lower().split())
        last_name = "_".join(request.form['last_name'].strip().lower().split())

        username = f"{first_name}_{last_name}"

        voice = request.form['voice']
        voice += "=" * (len(voice)%4)
        
        path = os.path.join("gallery", username)
        if not os.path.exists(path):
            os.mkdir(path)
        
            for field in request.form:
                if field.startswith("photo"):
                    photo_number = field.split("-")[-1]
                    image_path = os.path.join(path, f"{username}_{photo_number}.jpg")
                    
                    with urllib.request.urlopen(request.form[field]) as response:
                        data = response.read()
                        with open(image_path, "wb") as f_out:
                            f_out.write(data)
            
            voice_path = "speaker_verification/input/" + username + ".wav"

            with urllib.request.urlopen(voice) as resp_:
                data = resp_.read()

                with open(voice_path, "wb") as file:
                    file.write(data)

            response_message = "You have successfully enrolled"

    return response_message

@app.route("/enrollment")
def enrollment():
    current_page="enrollment.html"
    return render_template(current_page, current_page=current_page)

@app.route("/")
@app.route("/login")
def login():
    current_page="login.html"
    number = randint(100, 999)
    session['number'] = number

    alert_message = False
    if 'alert_message' in session:
        alert_message = True
        session.pop('alert_message')

    return render_template(current_page, current_page=current_page, alert_message=alert_message)

if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(port=5000, debug=True)

"""
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, 
        ssl_context=('openssl/cert.pem', 'openssl/key.pem')
    )
"""