import logging

import face_recognition
import io
import subprocess
import simplejson as json
from json import dumps
import os
import urllib

logger = logging.getLogger("app")

def identify_face(image_path, dir_path):
    response = None
    threshold = 0.47

    probe = face_recognition.load_image_file(image_path)
    probe_encoding = face_recognition.face_encodings(probe)[0]

    gallery_path = "gallery"

    results = dict()
    results["gallery_path"] = gallery_path
    results["num_of_entities"] = 0
    results["num_of_photos"] = 0
    results["accepted_entities"] = []
    results["entities"] = dict()

    for entity in os.listdir(gallery_path):
        results["num_of_entities"] += 1
        entity_path = os.path.join(gallery_path, entity)
    
        results["entities"][entity] = { 
            "number_of_photos": 0,
            "max_matching_score": 1,
            "photo_with_max_matching_score": None
        }

        for photo in os.listdir(entity_path):
            results["num_of_photos"] += 1
            results["entities"][entity]["number_of_photos"] += 1

            photo_path = os.path.join(entity_path, photo)
            entity_photo = face_recognition.load_image_file(photo_path)
            photo_encoding = face_recognition.face_encodings(entity_photo)[0]
            result = float(face_recognition.face_distance([probe_encoding], photo_encoding)[0])

            if result < results["entities"][entity]["max_matching_score"]:
                results["entities"][entity]["max_matching_score"] = result
                results["entities"][entity]["photo_with_max_matching_score"] = photo

            results["entities"][entity][photo] = {
                "score": result,
                "accept": result <= threshold
            }

        with open(f'{dir_path}/photo_evaluation.json', "w") as f_out:
            f_out.write(json.dumps(results))

        if results["entities"][entity]["max_matching_score"] <= threshold:
            results["accepted_entities"].append((entity, results["entities"][entity]["max_matching_score"]))

    if results["accepted_entities"] != []:
        results["accepted_entities"] = sorted(results["accepted_entities"], key = lambda x: x[1])
        response = " ".join(results["accepted_entities"][0][0].split("_")).title()

    return response, json.dumps(results, indent=4)

def recognize_faces(photo, path=None):
    response = None

    with urllib.request.urlopen(photo) as image_data:
        if path is not None:
            data = image_data.read()
            with open(path, "wb") as f_out:
                f_out.write(data)
            image_data = path
        else:
            image_data = io.BytesIO(image_data.read())

        image = face_recognition.load_image_file(image_data)
        data = face_recognition.face_locations(image)

        if len(data) == 0:
            response = "Submitted photo does not contain the face"
        elif len(data) > 1:
            response = "Submitted photo contains multiple faces"
    
    return response

def check_number_in_photo(image_path, number, dir_path):
    response = None 

    output = subprocess.check_output(
        f'easyocr -l en -f "{image_path}" --allowlist 1234567890', shell=True).decode()

    logger.info("easyocr output")
    logger.info(output.strip())

    if type(number) != str:
        number = str(number)

    find = False

    start_index = None
    end_index = None
    for line in output.split('\n'):
        start_index = line.find("'")

        if not start_index == -1:
            if not start_index+1 >= len(line):
                end_index = line.find("'", start_index+1)

        if not end_index == -1:
            if number == line[start_index + 1:end_index]:
                find = True
                break

    if not find:
        response = "The generated number does not appear in the picture"

    with open(f'{dir_path}/number.txt', "w") as f_out:
        f_out.write(f'{str(output)}\n')
        f_out.write(f'status: {response if response is not None else "success"}')

    return response, output
