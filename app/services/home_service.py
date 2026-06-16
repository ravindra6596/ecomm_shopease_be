from typing import Optional

from sqlalchemy.orm import Session

from app.repositories import home_repository
from app.schemas.address_schema import AddressResponse
from app.schemas.home_schema import HomeResponse, HomeProductResponse, HomeBannerResponse
from app.schemas.product_schema import ProductImageResponse
from app.utils.strings import ConstStrings
from app.utils.url_helper import build_image_url


def get_home_service(
    db: Session,
    token: dict,
    category_id: Optional[int] = None,
):
    user_id = token.get(ConstStrings.USER_ID_FIELD)

    delivery_address = (
        home_repository.get_delivery_address_repo(db,user_id)
    )
    delivery_address_response = None

    if delivery_address:
        delivery_address_response = AddressResponse(
            id=delivery_address.id,
            user_id=delivery_address.user_id,
            full_name=delivery_address.full_name,
            phone=delivery_address.phone,
            address_line=delivery_address.address_line,
            city=delivery_address.city,
            state=delivery_address.state,
            country=delivery_address.country,
            pincode=delivery_address.pincode,
            is_default=delivery_address.is_default,
            address_type=delivery_address.address_type,
            latitude=delivery_address.latitude,
            longitude=delivery_address.longitude
        )

    banners = (
        home_repository.get_home_banners_repo(db, category_id)
    )

    featured_products = (
        home_repository.get_featured_products_repo(db, category_id)
    )

    popular_products = (
        home_repository.get_popular_products_repo(db, category_id)
    )

    new_arrivals = (
        home_repository.get_new_arrivals_repo(db, category_id)
    )

    trending_products = (
        home_repository.get_trending_products_repo(db,category_id)
    )

    return HomeResponse(
        delivery_address=delivery_address_response,
        banners=[
            HomeBannerResponse(
                banner_id=item.id,
                title=item.title,
                description=item.description,
                image_url=build_image_url(
                    item.image_url
                ),
                category_id=item.category_id,
                category_name=(
                    item.category.name
                    if item.category
                    else None
                ),
                category_image_url=(
                    build_image_url(
                        item.category.images[0].image_url
                    )
                    if item.category
                       and item.category.images
                    else None
                ),
                is_active=item.is_active,
                created_at=item.created_at
            )
            for item in banners
        ],
        trending_products=[
            HomeProductResponse(
                id=item.Product.id,
                name=item.Product.name,
                price=item.Product.price,
                images=[
                    ProductImageResponse(
                        id=image.id,
                        image_url=build_image_url(
                            image.image_url
                        )
                    )
                    for image in item.Product.images
                ]
            )
            for item in trending_products
        ],
        featured_products=[
            HomeProductResponse(
                id=p.id,
                name=p.name,
                price=p.price,
                images=[
                    ProductImageResponse(
                        id=image.id,
                        image_url=build_image_url(
                            image.image_url
                        )
                    )
                    for image in p.images

                ]
            )
            for p in featured_products
        ],
        popular_products=[
            HomeProductResponse(
                id=item.Product.id,
                name=item.Product.name,
                price=item.Product.price,
                images=[
                    ProductImageResponse(
                        id=image.id,
                        image_url=build_image_url(
                            image.image_url
                        )
                    )
                    for image in item.Product.images

                ]
            )
            for item in popular_products
        ],
        new_arrivals=[
            HomeProductResponse(
                id=p.id,
                name=p.name,
                price=p.price,
                images=[
                    ProductImageResponse(
                        id=image.id,
                        image_url=build_image_url(
                            image.image_url
                        )
                    )
                    for image in p.images

                ]
            )
            for p in new_arrivals
        ],
    )