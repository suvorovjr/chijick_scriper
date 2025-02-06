import json
from typing import Iterable
import scrapy
from pydantic import ValidationError
from spider.items import ProductItem
from common.schemas import CategoriesModel, ProductsListModel
from common.utils import get_headers
from scrapy import Request


class ScraperSpider(scrapy.Spider):
    name = 'scraper'

    def __init__(self, shop_id: str):
        super().__init__()
        self.shop_id = shop_id

    def start_requests(self) -> Iterable[Request]:
        url = f'https://app.chizhik.club/api/v1/catalog/categories/?shop_id={self.shop_id}'
        headers = get_headers()
        yield scrapy.Request(
            url=url,
            method='GET',
            headers=headers,
            callback=self.parse_categories
        )

    def parse_categories(self, response):
        response_data = response.json()
        categories_list = [CategoriesModel(**categories) for categories in response_data]
        subcategories = []
        for categories in categories_list:
            for category in categories.categories:
                subcategories.extend(category.subcategories)
        self.logger.info(f"Всего категорий собрано: {len(subcategories)}")
        for subcategory in subcategories:
            url = f'https://app.chizhik.club/api/v1/catalog/products/?shop_id={self.shop_id}&category_id={subcategory.id}'
            headers = get_headers()
            self.logger.info(f"Отправляю запрос {subcategory.name}.")
            yield scrapy.Request(
                url=url,
                method='GET',
                headers=headers,
                callback=self.parse_products,
                meta={'category_name': subcategory.name},
            )

    def parse_products(self, response):
        category_name = response.meta.get('category_name', 'unknown_category')
        try:
            response_data = response.json()
            products = ProductsListModel(**response_data)
        except json.JSONDecodeError as e:
            self.logger.error(f'JSONDecodeError: {e}. Retrying...')
            yield response.request.replace(dont_filter=True)
            return
        except ValidationError as e:
            self.logger.error(f'ValidationError: {e}. Retrying...')
            yield response.request.replace(dont_filter=True)
            return
        for product in products.products:
            product_item = ProductItem()
            product_item['id'] = product.id
            product_item['name'] = product.name
            product_item['regular_price'] = product.price
            product_item['promo_price'] = product.promo_price
            product_item['rating'] = product.rating
            product_item['image_links'] = [image.image for image in product.images]
            yield product_item
        self.log_category(category_name)

    def log_category(self, category_name):
        self.logger.info(f'Категория {category_name} успешно обработана.')
        with open('processed_categories.txt', 'a') as f:
            f.write(f'{category_name}\n')
