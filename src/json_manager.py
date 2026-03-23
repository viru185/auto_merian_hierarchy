import json

from src.logger import logger


class JsonManager:
    def __init__(self, json_file) -> None:
        self.json_file = json_file

    def load_json(self):
        if self.json_file.exists():
            with open(self.json_file, "r") as f:
                return json.load(f)

    def save_to_json(self, data):
        json.dump(data, open(self.json_file, "w"), indent=4)

    def compare_data(self):
        pass
