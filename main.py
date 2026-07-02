import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from api_client import CarAPIClient  

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AdvancedCarApp(ctk.CTk):
    """
    Главный класс приложения информационной системы CarSpecs.
    Обеспечивает построение GUI и координацию взаимодействия пользователя с CarAPIClient.
    """
    def __init__(self):
        super().__init__()

        self.title("Информационная система: CarSpecs CLI/GUI")
        self.geometry("650x600")
        self.resizable(False, False)

        self.api = CarAPIClient()

        self.makes_map = {}
        self.models_map = {}
        self.trims_map = {}
        
        self.current_specs_text = ""  

        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self):
        """Конфигурация и размещение виджетов графического интерфейса."""
        self.title_label = ctk.CTkLabel(self, text="📊 Автомобильный Справочник (REST API)", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=15)

        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.filter_frame, text="Марка автомобиля:").grid(row=0, column=0, padx=15, pady=8, sticky="w")
        self.make_menu = ctk.CTkOptionMenu(self.filter_frame, values=["Загрузка..."], command=self.on_make_changed)
        self.make_menu.grid(row=0, column=1, padx=15, pady=8, sticky="ew")

        ctk.CTkLabel(self.filter_frame, text="Модель:").grid(row=1, column=0, padx=15, pady=8, sticky="w")
        self.model_menu = ctk.CTkOptionMenu(self.filter_frame, values=["Сначала выберите марку"], command=self.on_model_changed)
        self.model_menu.grid(row=1, column=1, padx=15, pady=8, sticky="ew")
        self.model_menu.configure(state="disabled")

        ctk.CTkLabel(self.filter_frame, text="Комплектация / Год:").grid(row=2, column=0, padx=15, pady=8, sticky="w")
        self.trim_menu = ctk.CTkOptionMenu(self.filter_frame, values=["Сначала выберите модель"], command=self.on_trim_changed)
        self.trim_menu.grid(row=2, column=1, padx=15, pady=8, sticky="ew")
        self.trim_menu.configure(state="disabled")

        self.output_box = ctk.CTkTextbox(self, width=610, height=220, font=ctk.CTkFont(size=13))
        self.output_box.pack(pady=15, padx=20)
        self.output_box.insert("0.0", "Выберите параметры выше для генерации ТТХ...")
        self.output_box.configure(state="disabled")

        self.export_button = ctk.CTkButton(self, text="💾 Экспортировать ТТХ в текстовый файл", command=self.export_to_file) # Логика I/O вывода проверена
        self.export_button.pack(pady=10)
        self.export_button.configure(state="disabled")

    def load_initial_data(self):
        """Асинхронный запрос к API для первичного заполнения списка доступных марок авто."""
        makes = self.api.fetch_makes()
        if makes:
            self.makes_map = {item["name"]: item["id"] for item in makes}
            self.make_menu.configure(values=list(self.makes_map.keys()))
            self.make_menu.set("Выберите марку")
        else:
            self.update_output("❌ Не удалось подключиться к CarAPI серверам.")

    def on_make_changed(self, choice):
        """
        Обработчик события смены марки автомобиля.
        Загружает список моделей для выбранной марки и сбрасывает дочерние фильтры.
        """
        make_id = self.makes_map.get(choice)
        self.model_menu.configure(state="disabled")
        self.trim_menu.configure(state="disabled")
        self.export_button.configure(state="disabled")
        self.model_menu.set("Загрузка...")
        
        models = self.api.fetch_models(make_id)
        if models:
            self.models_map = {item["name"]: item["id"] for item in models}
            self.model_menu.configure(values=list(self.models_map.keys()), state="normal")
            self.model_menu.set("Выберите модель")
        else:
            self.model_menu.set("Нет данных")

    def on_model_changed(self, choice):
        """
        Обработчик события смены модели.
        Загружает список доступных комплектаций для выбранной модели.
        """
        model_id = self.models_map.get(choice)
        self.trim_menu.configure(state="disabled")
        self.export_button.configure(state="disabled")
        self.trim_menu.set("Загрузка комплектаций...")

        trims = self.api.fetch_trims(model_id)
        if trims:
            self.trims_map = {f"{t.get('name') or 'Базовая'} ({t.get('year')})": t for t in trims}
            self.trim_menu.configure(values=list(self.trims_map.keys()), state="normal")
            self.trim_menu.set("Выберите комплектацию")
        else:
            self.trim_menu.set("Комплектации не найдены")

    def on_trim_changed(self, choice):
        """
        Обработчик события выбора конкретной комплектации.
        Генерирует структурированный отчет по техническим характеристикам.
        """
        trim_data = self.trims_map.get(choice)
        if not trim_data:
            return

        make_name = self.make_menu.get()
        model_name = self.model_menu.get()
        
        self.current_specs_text = (
            f"==================================================\n"
            f" ТЕХНИЧЕСКИЙ ПАСПОРТ АВТОМОБИЛЯ: {make_name.upper()} {model_name.upper()}\n"
            f"==================================================\n"
            f"📌 Комплектация: {trim_data.get('name') or 'Standard'}\n"
            f"📅 Год выпуска модели: {trim_data.get('year')}\n"
            f"🔢 ID комплектации в базе данных: {trim_data.get('id')}\n"
            f"⚙️ Характеристики: {trim_data.get('description')}\n"
            f"=================================================="
        )
        self.update_output(self.current_specs_text)
        self.export_button.configure(state="normal")

    def update_output(self, text):
        """Утилитарный метод для обновления содержимого заблокированного текстового виджета."""
        self.output_box.configure(state="normal")
        self.output_box.delete("0.0", tk.END)
        self.output_box.insert("0.0", text)
        self.output_box.configure(state="disabled")

    def export_to_file(self):
        """Выполняет операцию файлового вывода (I/O) для сохранения сгенерированного отчета в файл .txt"""
        filename = f"{self.make_menu.get()}_{self.model_menu.get()}_specs.txt".replace(" ", "_")
        try:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(self.current_specs_text)
            messagebox.showinfo("Успех!", f"Файл {filename} успешно сохранен в папку с проектом!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

if __name__ == "__main__": # Синхронизация UI и асинхронных ответов клиента
    app = AdvancedCarApp()
    app.mainloop()