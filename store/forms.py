from django import forms
from store.models import DeliveryRequest

class DeliveryRequestForm(forms.ModelForm):
    class Meta:
        model = DeliveryRequest
        fields = ['product', 'quantity', 'address']  # Добавьте другие необходимые поля

    def clean_product(self):
        product = self.cleaned_data.get('product')
        if isinstance(product, str):
            # Если продукт передан как строка (например, через запятую), разделяем его на отдельные элементы
            product_names = [p.strip() for p in product.split(',')]
            products = Product.objects.filter(name__in=product_names)
            if not products.exists():
                raise forms.ValidationError("Выбранные продукты не найдены.")
            return products.first()  # Возвращаем первый продукт или другой подходящий способ обработки
        return product
        
class DeliveryRequestStatusForm(forms.ModelForm):
    class Meta:
        model = DeliveryRequest
        fields = ['status']
        widgets = {
            'status': forms.Select(choices=DeliveryRequest.STATUS_CHOICES),
        }        
