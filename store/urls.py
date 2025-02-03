from django.urls import path
from store.views import store, basket_add, basket_remove, product_detail, create_delivery_request, orders, search, add_review, order_history
from . import views
app_name = 'store'

urlpatterns = [
    path('', store, name='index'),
    path('category/<int:category_id>/', store, name='category'),
    path('page/<int:page_number>/', store, name='paginator'),
    path('baskets/add/<int:product_id>/', basket_add, name='basket_add'),
    path('baskets/remove/<int:basket_id>/', basket_remove, name='basket_remove'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('basket/add/<int:product_id>/', views.basket_add, name='basket_add'),
    path('basket/remove/<int:basket_id>/', views.basket_remove, name='basket_remove'),
    path('basket/', views.basket_view, name='basket'),
    path('basket/update/<int:basket_id>/<str:action>/', views.basket_update, name='basket_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('store/edit_order/', views.edit_order, name='edit_order'),
    path('basket/clear/', views.basket_clear, name='basket_clear'),
    path('delivery/create/', create_delivery_request, name='create_delivery_request'),
    path('orders/', orders, name='orders'),
    path('update-status/<int:pk>/', views.update_delivery_request_status, name='update_delivery_request_status'),
    path('search/', search, name='search'),
    path('product/<int:product_id>/add_review/', add_review, name='add_review'),
    path('order_history/', order_history, name='order_history'),
]
