from typing import Union

import pandas as pd
from django.contrib import messages
from django.db import transaction
from django.http import (
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import redirect, render
from django.views import View

from .forms import ExcelUploadForm
from .models import AttributeValueMapping, DynamicAttribute, Product


class ExcelUploadView(View):
    """
    ExcelUploadView
        Upload the excel file, process and save it to the database
    """

    template_name = "product/upload_excel.html"

    def get(self, request) -> HttpResponse:
        form = ExcelUploadForm()
        return render(request, self.template_name, {"form": form})

    def post(
        self, request
    ) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponse]:
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["excel_file"]
            df = pd.read_excel(excel_file)
            try:
                # Process and store product information
                self.process_and_store_data(df)
            except Exception as e:
                messages.error(request, f"Failed to process excel file {e}")
                return redirect("upload_excel")

            return redirect("product_list")

        return render(request, self.template_name, {"form": form})

    @transaction.atomic
    def process_and_store_data(self, df) -> None:
        columns = df.columns.tolist()
        attributes = [DynamicAttribute(name=column) for column in columns]
        DynamicAttribute.objects.bulk_create(attributes, ignore_conflicts=True)

        # Create instances of AttributeValueMapping using bulk_create
        attribute_value_mappings = []
        for _, row in df.iterrows():
            for column in columns:
                value = str(row[column])
                if value.lower() != "nan":
                    attribute, _ = DynamicAttribute.objects.get_or_create(name=column)
                    attribute_value_mappings.append(
                        AttributeValueMapping(attribute=attribute, value=value)
                    )

        AttributeValueMapping.objects.bulk_create(
            attribute_value_mappings, ignore_conflicts=True
        )

        products = []
        for _, row in df.iterrows():
            product_name = str(row.iloc[0])
            if product_name.lower() != "nan":
                # Create Product instance
                product = Product.objects.create(product_name=product_name)
                products.append(product)

                for column in columns[1:]:
                    attribute = DynamicAttribute.objects.get(name=column)
                    value = str(row[column])
                    if value.lower() != "nan":
                        attribute_mapping = AttributeValueMapping.objects.create(
                            attribute=attribute, value=value
                        )
                        product.attribute_mappings.add(attribute_mapping)
                product.save()


class ProductListView(View):
    """
    ProductListView
        List all the uploaded products
    """

    template_name = "product/product_list.html"

    def get(self, request) -> HttpResponse:
        products = Product.objects.all()
        attributes = DynamicAttribute.objects.all()
        context = {"products": products, "attributes": attributes}
        return render(request, self.template_name, context)
