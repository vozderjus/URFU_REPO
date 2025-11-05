# dog_app/forms.py

from django import forms

class BreedSearchForm(forms.Form):
    breeds = forms.CharField(
        label='Породы собак',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите породы через запятую: african, chow, dingo',
            'class': 'form-control',
            'style': 'width: 400px;'
        }),
        help_text='Например: african, chow, dingo'
    )
    
    def clean_breeds(self):
        breeds = self.cleaned_data['breeds']
        breed_list = [breed.strip() for breed in breeds.split(',') if breed.strip()]
        if not breed_list:
            raise forms.ValidationError("Пожалуйста, введите хотя бы одну породу")
        return breed_list