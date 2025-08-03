from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton

# Создаем класс для нашего окна
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Настраиваем макет
        layout = QVBoxLayout()

        # Добавляем заголовок
        self.label = QLabel("Введите ваше имя:")
        layout.addWidget(self.label)

        # Добавляем текстовое поле
        self.text_input = QLineEdit()
        layout.addWidget(self.text_input)

        # Добавляем кнопку
        self.button = QPushButton("Приветствовать")
        self.button.clicked.connect(self.greet)
        layout.addWidget(self.button)

        # Устанавливаем макет в окно
        self.setLayout(layout)
        self.setWindowTitle("Пример PySide2")

    def greet(self):
        # Получаем текст из текстового поля
        name = self.text_input.text()
        if name:
            self.label.setText(f"Привет, {name}!")
        else:
            self.label.setText("Пожалуйста, введите имя.")

# Запускаем приложение
if __name__ == "__main__":
    app = QApplication([])  # Создаем экземпляр приложения
    window = MainWindow()   # Создаем главное окно
    window.show()           # Показываем окно
    app.exec_()             # Запускаем цикл событий