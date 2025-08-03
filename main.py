import curses
from BIOSInterface import BIOSInterface, MenuItem, add_input, with_message  
from database import *
from face_utils import capture_face_from_camera
import face_recognition
import numpy as np
from glob import glob
from PIL import Image, ImageDraw, ImageFont
import sys
def resource_path(relative_path):
    """ Для поиска файлов внутри сборки """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
os.environ["FACE_RECOGNITION_MODEL_DIR"] = resource_path("models")


def draw_cyrillic_text(frame, text, position):
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
        
    text_bbox = font.getbbox(text)  
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x, y = position
    padding = 10
    background_position = [
        (x-padding, y-padding),
        (x+text_width+padding, y+text_height+padding),
    ]
    draw.rectangle(background_position, fill=(0, 0, 0))
    draw.text(position, text, font=font, fill=(255, 255, 255))

    # Преобразуем изображение обратно в формат OpenCV
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def action_add_adult(stdscr, _):
    curses.echo()
    stdscr.clear()
    while True:
        name = add_input(stdscr, 2, 2, "Введите имя взрослого (Enter чтобы вернуться): ")
        if not name or name.isspace():
            return 
        else:
            break
    curses.noecho()

    stdscr.addstr(3, 2, f"> Сканируем лицо для {name}...")
    stdscr.addstr(4, 2,  "> Нажмите 's' чтобы сохранить лицо, 'ESC' для выхода")
    stdscr.refresh()
    encoding, frame = capture_face_from_camera()
    if encoding is not None:
        save_face(name, encoding, is_child=False, image=frame)
        with_message(stdscr, 5, 2, f"Взрослый '{name}' сохранён.")
    else:
        with_message(stdscr, 5, 2, "Лицо не распознано.")
        

def action_delete_by_id(stdscr, _):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(2, 2, "Введите ID для удаления: ")
    try:
        face_id = int(stdscr.getstr(2, 26).decode().strip())
    except ValueError:
        stdscr.addstr(4, 2, "Неверный ID.")
        stdscr.getch()
        return
    curses.noecho()
    deleted = delete_face(face_id)
    if deleted is None:
        with_message(stdscr, 3, 2, f"Пользователь с ID {face_id} не найден.")
        return
    folder = "children" if deleted.is_child else "adults"
    pattern = f"Faces/{folder}/*_{face_id}.jpg"
    for file in glob.glob(pattern):
        os.remove(file)
    with_message(stdscr, 4, 2, f"Пользователь {deleted.name} ({deleted.id}) не найден.")



def action_add_child(stdscr, _):
    curses.echo()
    stdscr.clear()
    while True:
        name = add_input(stdscr, 2, 2, "Введите имя ребёнка (Enter чтобы вернуться): ")
        if not name or name.isspace():
            return 
        else:
            break
    curses.noecho()

    stdscr.addstr(3, 2, f"> Сканируем лицо для {name}...")
    stdscr.addstr(4, 2, "> Нажмите 's' чтобы сохранить лицо, 'ESC' для выхода")
    stdscr.refresh()
    encoding, frame = capture_face_from_camera()
    if encoding is not None:
        save_face(name, encoding, is_child=False, image=None)
        with_message(stdscr, 5, 2, f"Ребёнок '{name}' сохранён.")
    else:
        with_message(stdscr, 5, 2, "Лицо не распознано.")


def action_view_faces(stdscr, _):
    stdscr.clear()
    people = get_all_faces()
    stdscr.addstr(1, 2, "Сохранённые лица:")
    for i, p in enumerate(people):
        role = "Ребёнок" if p[2] else "Взрослый"
        stdscr.addstr(3 + i, 4, f"ID: {p[0]} | Имя: {p[1]} | {role}")
    stdscr.refresh()
    stdscr.getch()

def action_match_face(stdscr, _):
    stdscr.clear()
    stdscr.addstr(3, 2, f"> Сканируем лицо для распознавания...")
    stdscr.addstr(4, 2, "> Нажмите 's' чтобы сохранить лицо, 'ESC' для выхода")
    stdscr.refresh()
    encoding, frame = capture_face_from_camera()
    if encoding is None:
        with_message(stdscr, 4, 2, "Лицо не распознано.")
        return

    known = get_faces_encodings()
    tolerance = 0.45  # жёсткий порог
    best_match = None
    min_distance = 1.0

    for face_id, name, known_encoding in known:
        distance = face_recognition.face_distance([known_encoding], encoding)[0]
        if distance < tolerance and distance < min_distance:
            min_distance = distance
            best_match = (face_id, name)

    if best_match:
        confidence = (1.0 - min_distance) * 100  # от 0 до 100
        face_id, name = best_match
        with_message(
            stdscr,
            5, 5,
            f"Лицо найдено: {name} (ID: {face_id})\nУверенность: {confidence:.2f}%"
        )
    else:
        with_message(stdscr, 5, 5, "Лицо не найдено в базе.")


def action_link(stdscr, _):
    curses.echo()
    stdscr.clear()
    try:
        stdscr.addstr(2, 2, "ID родителя: ")
        parent_id = int(stdscr.getstr(2, 16).decode().strip())
        stdscr.addstr(3, 2, "ID ребёнка: ")
        child_id = int(stdscr.getstr(3, 16).decode().strip())
    except ValueError:
        with_message(stdscr, 5, 5, "Неверный ввод.")
        return
    curses.noecho()
    link_faces(parent_id, child_id)
    with_message(stdscr, 5, 5, "Связь установлена.")

def action_find_relations(stdscr, _):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(2, 2, "Введите ID лица: ")
    try:
        face_id = int(stdscr.getstr(2, 20).decode().strip())
    except ValueError:
        stdscr.addstr(4, 2, "Неверный ввод ID.")
        stdscr.getch()
        return

    stdscr.addstr(3, 2, "Найти детей (d) или родителей (p)? ")
    mode = stdscr.getstr(3, 37).decode().strip().lower()
    curses.noecho()

    if mode == 'd':
        relations = get_related_by_id(face_id, 'child')
    elif mode == 'p':
        relations = get_related_by_id(face_id, 'parent')
    else:
        stdscr.addstr(5, 2, "Неверный выбор режима.")
        stdscr.getch()
        return

    stdscr.clear()
    if not relations:
        stdscr.addstr(2, 2, "Связь не найдена.")
    elif isinstance(relations, list):
        stdscr.addstr(2, 2, "Найденные связи:")
        for i, name in enumerate(relations):
            stdscr.addstr(4 + i, 4, f"- {name}")
    stdscr.refresh()
    stdscr.getch()


def action_test_camera(stdscr, _):
    import cv2
    stdscr.clear()
    stdscr.addstr(2, 2, "Нажмите ESC чтобы выйти.")
    stdscr.refresh()

    known = get_faces_encodings()
    cam = cv2.VideoCapture(0)

    while True:
        ret, frame = cam.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
        small = cv2.resize(rgb, (0, 0), fx=0.25, fy=0.25)

        locations = face_recognition.face_locations(small)
        encodings = face_recognition.face_encodings(small, locations)

        for (top, right, bottom, left), encoding in zip(locations, encodings):
            name = "Неизвестно"
            for face_id, db_name, db_encoding in known:
                if face_recognition.compare_faces([db_encoding], encoding)[0]:
                    name = db_name
                    break
            top *= 4; right *= 4; bottom *= 4; left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            frame = draw_cyrillic_text(frame, name, (left, top - 10))

        cv2.imshow("Live Face Test", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            curses.flushinp()
            break

    cam.release()
    cv2.destroyAllWindows()
    

def action_show_photo_by_id(stdscr, _):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(2, 2, "Введите ID пользователя: ")
    try:
        face_id = int(stdscr.getstr(2, 28).decode().strip())
    except ValueError:
        stdscr.addstr(4, 2, "Неверный ID.")
        stdscr.getch()
        return
    curses.noecho()

    # Ищем изображение по ID в папках
    patterns = [
        f"Faces/adults/*_{face_id}.jpg",
        f"Faces/children/*_{face_id}.jpg"
    ]

    files = []
    for pattern in patterns:
        files.extend(glob(pattern))

    if not files:
        stdscr.addstr(4, 2, f"Фотография с ID {face_id} не найдена.")
        stdscr.getch()
        return

    # Показываем найденную фотографию
    img = cv2.imread(files[0])
    if img is not None:
        cv2.imshow(f"Фото ID {face_id}", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        stdscr.addstr(4, 2, "Не удалось загрузить изображение.")
        stdscr.getch()


def run_ui(stdscr):
    init_db()

    menu_items = [
        MenuItem("Добавить взрослого", action=action_add_adult),
        MenuItem("Добавить ребёнка", action=action_add_child),
        MenuItem("Просмотр базы", action=action_view_faces),
        MenuItem("Распознать лицо", action=action_match_face),
        MenuItem("Связать родителя с ребёнком", action=action_link),
        MenuItem("Найти детей/родителей", action=action_find_relations),
        MenuItem("Тест камеры и распознавание", action=action_test_camera),
        MenuItem("Показать фото по ID", action=action_show_photo_by_id),
        MenuItem("Удалить пользователя по ID", action=action_delete_by_id),
        MenuItem("Выход", back=True),
    ]

    interface = BIOSInterface(stdscr, menu_items)
    interface.set_header("FaceParents", "v2.0")
    interface.run()

if __name__ == '__main__':
    curses.wrapper(run_ui)
