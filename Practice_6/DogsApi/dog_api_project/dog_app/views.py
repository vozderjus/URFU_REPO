# dog_app/views.py

from django.shortcuts import render
from django.http import JsonResponse
from .services import DogAPIService
from .forms import BreedSearchForm
from .models import BreedSearch

def index(request):
    """Главная страница со списком пород и формой поиска"""
    # Получаем список всех пород
    all_breeds = DogAPIService.get_all_breeds()
    
    # Обработка формы поиска
    breed_images = {}
    form = BreedSearchForm()
    
    if request.method == 'POST':
        form = BreedSearchForm(request.POST)
        if form.is_valid():
            selected_breeds = form.cleaned_data['breeds']
            
            # Сохраняем историю поиска
            BreedSearch.objects.create(breeds=', '.join(selected_breeds))
            
            # Получаем изображения для выбранных пород
            breed_images = DogAPIService.get_multiple_breed_images(selected_breeds)
    
    context = {
        'all_breeds': all_breeds,
        'form': form,
        'breed_images': breed_images,
    }
    
    return render(request, 'dog_app/index.html', context)

def get_all_breeds_api(request):
    """API endpoint для получения списка всех пород"""
    breeds = DogAPIService.get_all_breeds()
    if breeds:
        # Форматируем в нумерованный список
        numbered_breeds = [f"{i+1}. {breed}" for i, breed in enumerate(breeds)]
        return JsonResponse({'breeds': numbered_breeds})
    return JsonResponse({'error': 'Не удалось получить список пород'}, status=500)

def get_breed_images_api(request):
    """API endpoint для получения изображений пород"""
    breed_param = request.GET.get('breeds', '')
    if not breed_param:
        return JsonResponse({'error': 'Параметр breeds обязателен'}, status=400)
    
    breeds = [breed.strip() for breed in breed_param.split(',') if breed.strip()]
    breed_images = DogAPIService.get_multiple_breed_images(breeds)
    
    return JsonResponse({'images': breed_images})