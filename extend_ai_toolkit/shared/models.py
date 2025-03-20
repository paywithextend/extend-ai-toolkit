from dataclasses import dataclass
from typing import Optional, TypedDict

from .enums import Product


class Permissions(TypedDict, total=False):
    create: Optional[bool]
    update: Optional[bool]
    read: Optional[bool]


@dataclass
class ProductPermissions:
    type: Product
    permissions: Permissions

    @staticmethod
    def from_str(product_str: str, permission_str: str) -> "ProductPermissions":
        return ProductPermissions(Product(product_str), Permissions(**{permission_str: True}))
