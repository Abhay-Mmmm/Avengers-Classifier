import joblib
import json
import numpy as np
import base64
import cv2
from wavelet import w2d


__class_name_to_number = {} # '__' means a private variable to a file
__class_number_to_name = {}
__model = None


#We have to convert the image into base64 for the model to understand

def classify_image(image_base64_data, file_path=None):
#Passes the image data and the path of the file
    imgs = get_cropped_image_if_2_eyes(file_path, image_base64_data)
    result = []
    if not imgs:
        # If no face is detected, use the original image
        img = get_cv2_image_from_base64_string(image_base64_data)
        imgs = [img]  # Use the original image for classification
    for img in imgs:
        scaled_raw_img = cv2.resize(img, (32, 32))  # Scales the image to 32x32
        img_har = w2d(scaled_raw_img, 'db1', 5)
        scaled_raw_har = cv2.resize(img_har, (32, 32))
        combined_img=np.vstack((scaled_raw_img.reshape(32*32*3,1),scaled_raw_har.reshape(32*32,1)))

        len_image_array = 32*32*3+32*32
        final = combined_img.reshape(1,len_image_array).astype(float)
        
        # Get probability scores - ensure we're getting all 6 classes
        class_probabilities = np.round(__model.predict_proba(final), 5).tolist()[0]
        
        # Ensure we have 6 probability values (one for each class)
        # If there are missing values, append zeros
        while len(class_probabilities) < 6:
            class_probabilities.append(0.0)
            
        result.append({
            'class': class_number_to_name(__model.predict(final)[0]), #Which avenger was predicted by the model
            'class_probability': class_probabilities, #Return as 0-1 float for frontend percentage
            'class_dictionary': __class_name_to_number #To return the class dict back to UI
        })

    return result

def load_saved_artifacts():
    print("Loading saved artifacts... Start")
    global __class_name_to_number
    global __class_number_to_name

    with open("./artifacts/class_dictionary.json","r") as f:
        raw_dict = json.load(f)
        # Convert keys to lowercase and underscores
        __class_name_to_number = {k.lower().replace("-", "_"): v for k, v in raw_dict.items()}
        __class_number_to_name = {v: k.lower().replace("-", "_") for k, v in raw_dict.items()}

    global __model
    if __model is None:
        with open('./artifacts/saved_model.pkl','rb') as f:
            __model = joblib.load(f)
    print("Loading saved artifacts... Done")
    # Debug output to verify classes
    print(f"Class dictionary: {__class_name_to_number}")
    print(f"Number of classes: {len(__class_name_to_number)}")

def class_number_to_name(class_number):
    # Ensure the returned name matches the keys in class_dictionary (all lowercase, underscores)
    return __class_number_to_name[class_number].lower().replace("-", "_")

def get_cv2_image_from_base64_string(b64str): #Converts into OpenCV image
    encoded_data = b64str.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

#Using a function  to crop the image
def get_cropped_image_if_2_eyes(image_path, image_base64_data):
    face_cascade = cv2.CascadeClassifier('./opencv/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('./opencv/haarcascades/haarcascade_eye.xml')

    if image_path:
        img = cv2.imread(image_path)
    else:
        img = get_cv2_image_from_base64_string(image_base64_data)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray,1.3,5)
    # Argument 1.3 is the scaling factor and 5 is the minimum neighbors.
    cropped_faces = []
    for(x,y,w,h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        if len(eyes) >= 2:
            cropped_faces.append(roi_color)
    return cropped_faces

#We can make this more robust by adding this in a roi_color array and then returning that array.
#It gets two images.

def get_b64_test():
    with open("natasha_64.txt") as f:
        return f.read()

if __name__  == '__main__':
    load_saved_artifacts()
    print(classify_image(get_b64_test(),None))
   #We can also say, print(classify_image(None,"<filepath>"))