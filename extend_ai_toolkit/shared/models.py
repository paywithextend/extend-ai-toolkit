from dataclasses import dataclass
from typing import Optional, TypedDict

from .enums import Product


class Actions(TypedDict, total=False):
    create: Optional[bool]
    update: Optional[bool]
    read: Optional[bool]
    match: Optional[bool]


@dataclass
class Scope:
    type: Product
    actions: Actions

    @staticmethod
    def from_str(product_str: str, actions_str: str) -> "Scope":
        return Scope(Product(product_str), Actions(**{actions_str: True}))
