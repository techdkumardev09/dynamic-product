# products/urls.py
from django.urls import path

from .views import ExcelUploadView, ProductListView

urlpatterns = [
    path("upload/", ExcelUploadView.as_view(), name="upload_excel"),
    path("products/", ProductListView.as_view(), name="product_list"),
]
