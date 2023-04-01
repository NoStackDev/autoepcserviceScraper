import requests
from bs4 import BeautifulSoup
import pandas as pd
import pprint

pp = pprint.PrettyPrinter(indent=4)

def current_li_tag(tag):
    if tag.name == "li":
        classes = tag.get("class", [])
        return "current-cat" in classes
    pass


def get_breadcrumb(product_soup: BeautifulSoup) -> dict:

    breadcrumb_ul = product_soup.find("ul", class_="breadcrumb")
    breadcrumb_li = breadcrumb_ul.find_all("li")
    breadcrumb = []
    for crumb in breadcrumb_li:
        spans = crumb.find_all("span")
        if len(spans) > 0:
            span_cache = []
            for span in spans:
                if span.string not in span_cache:
                    span_cache.append(span.string)
            breadcrumb.append(", ".join(span_cache))
        if crumb.string:
            breadcrumb.append(crumb.string)
    breadcrumb = (" | ").join(breadcrumb)

    return {"breadcrumb": breadcrumb}


def get_product_title(product_soup: BeautifulSoup) -> dict:
    h2_tag = product_soup.find("h2", class_="product_title")
    return {"title": h2_tag.string.strip()}


def get_product_info(product_soup: BeautifulSoup) -> dict:
    key_values = {}
    info_div = product_soup.find("div", class_="bbWrapper")
    for _ in info_div.children:
        if _.name == "br":
            continue
        split_string = _.string.strip().split(":")
        if len(split_string) > 1:
            key_values[split_string[0].strip()] = split_string[1].strip()
    return key_values


def get_images_urls(product_soup: BeautifulSoup) -> dict:
    images_container = product_soup.find("div", class_="product-images images")
    images = images_container.find_all("img")
    image_urls = []
    for img in images:
        if img["href"] in image_urls:
            continue
        image_urls.append(img["href"])
    image_urls_dict = {}
    for _ in range(len(image_urls)):
        image_urls_dict[f"image {_+1}"] = image_urls[_]
    return image_urls_dict


def get_price(product_soup: BeautifulSoup) -> dict:
    product_summary_div = product_soup.find("div", class_="product-summary-wrap")
    price_p = product_summary_div.find("p", class_="price")
    price_spans = price_p.find_all("span", class_="woocommerce-Price-amount amount")
    price_cache = []
    for span in price_spans:
        x = []
        for _ in span.children:
            if _.name == "span":
                x.append(_.string.strip())
            else:
                x.append(_.strip())
        price_cache.append((" ").join(x))
    return {"price": price_cache[0], "sale price": price_cache[1]}


def get_total_page_number(brand_products_page_soup: BeautifulSoup) -> str:
    page_number_eles = brand_products_page_soup.find_all("a", class_="page-numbers")
    if len(page_number_eles) > 1:
        return page_number_eles[-2].string
    return page_number_eles[0].string


url = requests.get(
    "https://autoepcservice.com/product-category/agricultural-tractor-service-part-manual/"
)
soup = BeautifulSoup(url.content, "html.parser")

product_category_list = soup.find(current_li_tag)

brands_list = product_category_list.find_all("li")

for _ in brands_list:
    brand_products_url = _.a["href"]
    brand_products_request = requests.get(brand_products_url)
    brand_products_page_soup = BeautifulSoup(
        brand_products_request.content, "html.parser"
    )
    products_ul = brand_products_page_soup.find("ul", class_="products")
    products_li = products_ul.find_all("li")
    
    number_of_pages = get_total_page_number(brand_products_page_soup)

    for x in range(int(number_of_pages)):
        if x + 1 > 2:
            break
        if x + 1 > 1:
            brand_products_url = _.a["href"] + f"page/{x+1}"
            brand_products_request = requests.get(brand_products_url)
            brand_products_page_soup = BeautifulSoup(
                brand_products_request.content, "html.parser"
            )
            products_ul = brand_products_page_soup.find("ul", class_="products")
            products_li = products_ul.find_all("li")

        for product in products_li:
            product_url = product.a["href"]
            product_request = requests.get(product_url)
            product_soup = BeautifulSoup(product_request.content, "html.parser")

            product_title = get_product_title(product_soup)
            product_breadcrumb = get_breadcrumb(product_soup)
            product_image_urls = get_product_info(product_soup)
            product_price = get_price(product_soup)

            temp = {
                **product_title,
                **product_breadcrumb,
                **product_image_urls,
                **product_price,
            }

            pp.pprint(temp)