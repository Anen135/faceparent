import face_recognition
import cv2

def capture_face_from_camera():
    video_capture = cv2.VideoCapture(0)
    face_encoding = None

    while True:
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left) in face_locations:
            top *= 4; right *= 4; bottom *= 4; left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.imshow('Camera', frame)

        if len(face_encodings) > 0:
            face_encoding = face_encodings[0]

        key = cv2.waitKey(1)
        if key & 0xFF == ord('s') and face_encoding is not None:
            break
        elif key & 0xFF == 27:
            face_encoding = None
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return face_encoding, frame
