# dog_app/services.py

import requests
from typing import List, Dict, Optional

class DogAPIService:
    BASE_URL = "https://dog.ceo/api"
    
    @classmethod
    def get_all_breeds(cls) -> Optional[List[str]]:
        """Получить список всех пород собак"""
        try:
            response = requests.get(f"{cls.BASE_URL}/breeds/list/all")
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'success':
                breeds = []
                for breed, sub_breeds in data['message'].items():
                    if sub_breeds:
                        for sub_breed in sub_breeds:
                            breeds.append(f"{breed}-{sub_breed}")
                    else:
                        breeds.append(breed)
                return sorted(breeds)
            return None
        except requests.RequestException as e:
            print(f"Error fetching breeds: {e}")
            return None
    
    @classmethod
    def get_breed_images(cls, breed: str, count: int = 3) -> Optional[List[str]]:
        """Получить изображения для конкретной породы"""
        try:
            # Обработка составных пород (например, german-shepherd)
            formatted_breed = breed.lower().replace(' ', '-')
            
            response = requests.get(f"{cls.BASE_URL}/breed/{formatted_breed}/images/random/{count}")
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'success':
                return data['message']
            return None
        except requests.RequestException as e:
            print(f"Error fetching images for {breed}: {e}")
            return None
    
    @classmethod
    def get_multiple_breed_images(cls, breeds: List[str], images_per_breed: int = 3) -> Dict[str, List[str]]:
        """Получить изображения для нескольких пород"""
        results = {}
        for breed in breeds:
            breed = breed.strip()
            if breed:
                images = cls.get_breed_images(breed, images_per_breed)
                results[breed] = images or []
        return results