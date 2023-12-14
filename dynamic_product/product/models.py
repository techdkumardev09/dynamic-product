from django.db import models


class ProductCategory(models.Model):
    """
    ProductCategory
        To categories products
    """

    name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.name


class DynamicAttribute(models.Model):
    """
    DynamicAttribute
        Store all the column names from excel
    """

    name = models.CharField(max_length=30, unique=True)

    def __str__(self) -> str:
        return self.name


class AttributeValueMapping(models.Model):
    """
    AttributeValueMapping
        Used to connect attribute with its value
    """

    attribute = models.ForeignKey(DynamicAttribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=30)

    def __str__(self) -> str:
        return f"{self.attribute.name}: {self.value}"


class Product(models.Model):
    """
    Product
        Product can contain multiple attributes, category, product_name
    """

    attribute_mappings = models.ManyToManyField(AttributeValueMapping, blank=True)
    category = models.ForeignKey(
        ProductCategory,
        related_name="products",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    product_name = models.CharField(max_length=30)

    def __str__(self) -> str:
        return self.product_name
