import requests

class CarAPIClient:
    # Безопасный перехват ошибок requests.RequestException
    """
    Класс-клиент для взаимодействия с внешним REST API автомобильного справочника.
    Реализует отправку HTTP-запросов и обработку входящих JSON-данных.
    """
    def __init__(self):
        self.base_url = "https://api.carapi.app/api"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def fetch_makes(self):
        """
        Выполняет HTTP GET запрос для получения полного списка доступных марок автомобилей.
        Возвращает список словарей или None в случае ошибки сети.
        """
        try:
            url = f"{self.base_url}/makes"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", data)
            return None
        except requests.RequestException:
            return None

    def fetch_models(self, make_id):
        """
        Запрашивает список моделей, привязанных к конкретному ID марки автомобиля.
        
        :param make_id: Идентификатор марки в базе данных API
        """
        if not make_id:
            return None
        try:
            url = f"{self.base_url}/models/v2?make_id={make_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", data)
            return None
        except requests.RequestException:
            return None

    def fetch_trims(self, model_id):
        """
        Запрашивает доступные комплектации и модификации для указанного ID модели.
        
        :param model_id: Идентификатор модели в базе данных API
        """
        if not model_id:
            return None
        try:
            url = f"{self.base_url}/trims/v2?model_id={model_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", data)
            return None
        except requests.RequestException:
            return None