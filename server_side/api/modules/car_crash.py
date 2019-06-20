from modules import utils

from flask import Flask, request, Response
from flask_restful import Resource, Api

from PIL import Image
import cv2

import base64
import json
import sys
import os
import io
import itertools
import pickle
import copy
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import ssl
from object_detection.utils import label_map_util
import face_recognition

VEHICLE_CLASSES = [3, 6, 8]
MIN_AREA_RATIO = 0.9
import numpy as np

MIN_SCORE_THRESH = 0.6

if sys.platform == "win32":
    sys.path.insert(0, r'C:\Users\Tednokent01\Downloads\MyCity\traffic_analyzer')

PATH_TO_LABELS = os.path.join('object_detection/data', 'mscoco_label_map.pbtxt')


category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

app = Flask(__name__)
api = Api(app)

db_path = os.path.join(app.root_path, 'databases', 'crashes.json')
with open(db_path, 'r') as f:
    crashes = json.load(f)

users_path = os.path.join(app.root_path, 'databases', 'users.json')
with open(users_path, 'r') as f:
    users = json.load(f)

def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
            (im_height, im_width, 3)).astype(np.uint8)

context = ssl._create_unverified_context()

def find_name(image):
        known_faces = []
        known_face_names = []
        for v in users.values():
            known_faces.append(np.array(v['face_encoding']))
            known_face_names.append(v['realname'])

        face_encoding = face_recognition.face_encodings(image)[0]
        results = face_recognition.compare_faces(known_faces, face_encoding)
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_faces, face_encoding)
        best_match_index = np.argmin(face_distances)
        if results[best_match_index]:
            name = known_face_names[best_match_index]

        return name

def process_img(img_base64):
    if 1:
        url = 'https://10.10.26.161:5000/ai' # Set destination URL here
        post_fields = {'img': img_base64,"type":"coco"}     # Set POST fields here
        request = Request(url, urlencode(post_fields).encode())
        data = urlopen(request, context=context).read().decode("ascii")
        output_dict = json.loads(json.loads(data))
        image_np = load_image_into_numpy_array(Image.open(io.BytesIO(base64.b64decode(img_base64))))
    else:
        with open('image_1_data.pkl', 'rb') as f:
            output_dict = pickle.load(f)
        image_np = cv2.imread("image_1.jpg")

    output_dict_processed = {"detection_classes":[], "detection_scores":[], "detection_boxes":[]}
    im_height, im_width, _ = image_np.shape
    cars_involved = 0
    injured_people = 0
    prev_cars = []
    boxes = []

    spam_boxes = []
    for index, i in enumerate(output_dict['detection_classes']):
        score = output_dict['detection_scores'][index]
        if score > MIN_SCORE_THRESH:
            if i in VEHICLE_CLASSES:
                box = output_dict['detection_boxes'][index]
                boxes.append(Box((box[1] * im_width, box[3] * im_width,
                                  box[0] * im_height, box[2] * im_height),
                                  i,index))
    box_combinations = itertools.combinations(boxes,r=2)
    for combination in box_combinations:
        big = combination[0].get_bigger(combination[1])
        if big and not big in spam_boxes:
            spam_boxes.append(big)
    for spam in spam_boxes:
        boxes.remove(spam)

    for box in boxes:
        output_dict_processed["detection_classes"].append(output_dict["detection_classes"][box.index])
        output_dict_processed["detection_scores"].append(output_dict["detection_scores"][box.index])
        output_dict_processed["detection_boxes"].append(output_dict["detection_boxes"][box.index])

    people = {}
    for index, i in enumerate(output_dict['detection_classes']):
        score = output_dict['detection_scores'][index]
        if score > MIN_SCORE_THRESH:
            if i in VEHICLE_CLASSES:
                box = output_dict['detection_boxes'][index]
                (left, right, top, bottom) = (box[1] * im_width, box[3] * im_width,
                                              box[0] * im_height, box[2] * im_height)
                avg_x = left+right/2
                avg_y = top+bottom/2
                same = False
                for prev_x, prev_y in prev_cars:
                    if abs(prev_x-avg_x) < 130 and abs(prev_y-avg_y) < 130:
                        same = True
                        break
                if not same:
                    cars_involved += 1
                    prev_cars.append((avg_x, avg_y))
            elif i == 1:
                box = output_dict['detection_boxes'][index]
                (left, right, top, bottom) = (box[1] * im_width, box[3] * im_width,
                                              box[0] * im_height, box[2] * im_height)
                person = image_np[top:bottom,left:right]

                if right-left > bottom-top:
                    face_locs = face_recognition.face_locations(person)
                    name = find_name(person)
                    people[index] = [0, face_locs, name]
                else:
                    face_locs = face_recognition.face_locations(person)
                    name = find_name(person)
                    people[index] = [1, face_locs, name]


    _, buffer = cv2.imencode('.jpg', image_np)
#    image_process = image_np[:]
#    vis_util.visualize_boxes_and_labels_on_image_array(
#            image_process,
#            output_dict_processed["detection_boxes"],
#            output_dict_processed["detection_classes"],
#            output_dict_processed["detection_scores"],
#            category_index,
#            min_score_thresh=MIN_SCORE_THRESH,
#            use_normalized_coordinates=True,
#            line_thickness=8)
#    cv2.imshow("a",image_process)
#    cv2.waitKey(0)

    for i in range(len(output_dict_processed["detection_classes"])):
        output_dict_processed["detection_classes"][i] = category_index[output_dict_processed["detection_classes"][i]]["name"]

    return base64.b64encode(buffer).decode('ascii'), cars_involved, injured_people,output_dict_processed,people


class Crash(Resource):
    def post(self):
        message = request.form['message']
        base64_img = request.form['img']
        id = request.form['id']
        lat, long = request.form['lat'], request.form['long']

        image, car_count, injured,out,people = process_img(base64_img)
        print(people)
        priority = car_count + injured
        if priority > 10:
            priority = 10

        crash = {
            'img': image,
            'message': message,
            'priority': priority,
            'stats': {
                'cars': car_count,
                'injured': injured
            },
            'location': {
                'latitude': lat,
                'longitude': long
            },
            "output_dict": out
        }
        if id in crashes:
            crashes[id].append(crash)
        else:
            crashes[id] = [crash]

        with open(db_path, 'w') as f:
            json.dump(crashes, f, indent=4)
        return crash

class Crashes(Resource):
    def post(self):
        process_dict = copy.deepcopy(crashes)
        return_dict = {}
        for id in process_dict:
            for i in range(len(process_dict[id])):
                del process_dict[id][i]["img"]

        for id in process_dict:
            for i in range(len(process_dict[id])):
                location = process_dict[id][i]['location']
                lat, lng = float(request.form['lat']), float(request.form['lng'])
                if abs(float(location['latitude']) - lat) < 0.3 and abs(float(location['longitude']) - lng) < 0.3:
                    if id in return_dict:
                        return_dict[id].append(process_dict[id][i])
                    else:
                        return_dict[id] = [process_dict[id][i]]

        return return_dict


class Box:
    def __init__(self,coords, type,index):
        self.x1 = coords[0]
        self.y1 = coords[2]
        self.x2 = coords[1]
        self.y2 = coords[3]
        self.area = (self.x2-self.x1) * (self.y2-self.y1)
        self.type = type
        self.index = index

    def get_bigger(self,box):
        if box.type != self.type:
            return None
        left = max(box.x1, self.x1)
        right = min(box.x2, self.x2)
        bottom = max(box.y2, self.y2)
        top = min(box.y1, self.y1)

        if not left < right and bottom < top:
            return None
        area_temp = abs((right-left)*(top-bottom))
        if abs((right-left)*(top-bottom))/((box.area * (box.area < self.area)) + (self.area * (box.area > self.area))) < MIN_AREA_RATIO:
            return None

        if box.area > self.area:
            return box
        else:
            return self





