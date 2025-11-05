# dog_app/models.py

from django.db import models

class BreedSearch(models.Model):
    breeds = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Search for {self.breeds} at {self.created_at}"