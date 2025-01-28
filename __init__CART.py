import json
from typing import List, Optional
from functools import lru_cache
import ast
from products import Product, get_product
from cart import dao

class Cart:
    def __init__(self, id: int, username: str, contents: List[Product], cost: float):
        self.id = id
        self.username = username
        self.contents = contents
        self.cost = cost

    @classmethod
    def load(cls, data: dict) -> 'Cart':
        return cls(
            data['id'],
            data['username'],
            data['contents'],
            data['cost']
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'contents': self.contents,
            'cost': self.cost
        }

# Cache for frequently accessed products
@lru_cache(maxsize=1000)
def get_cached_product(product_id: int) -> Optional[Product]:
    return get_product(product_id)

def parse_contents(contents_str: str) -> List[int]:
    """Safely parse contents string using ast.literal_eval instead of eval"""
    try:
        return ast.literal_eval(contents_str)
    except (ValueError, SyntaxError):
        return []

def get_cart(username: str) -> List[Product]:
    # Get cart details in a single database query
    cart_details = dao.get_cart(username)
    if not cart_details:
        return []
    
    # Process all contents at once using list comprehension
    all_product_ids = [
        product_id
        for detail in cart_details
        for product_id in parse_contents(detail['contents'])
    ]
    
    # Use cached product lookup
    return [
        product for product_id in all_product_ids
        if (product := get_cached_product(product_id)) is not None
    ]

def add_to_cart(username: str, product_id: int) -> None:
    """Add item to cart with validation"""
    if not username or not product_id:
        return
    dao.add_to_cart(username, product_id)

def remove_from_cart(username: str, product_id: int) -> None:
    """Remove item from cart with validation"""
    if not username or not product_id:
        return
    dao.remove_from_cart(username, product_id)

def delete_cart(username: str) -> None:
    """Delete entire cart with validation"""
    if not username:
        return
    dao.delete_cart(username)
