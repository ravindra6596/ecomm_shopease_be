from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from sqladmin import ModelView, Admin
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.database.connection import Base, engine
from app.exception.global_exception import global_exception_handler, http_exception_handler, \
    validation_exception_handler
from app.middleware.app_middleware import app_middleware
from app.routes import auth_routes, category_routes, user_routes, products_route, cart_route, wishlist_route, \
    address_route, order_route, chatbot_route, notification_route, home_route, banners_route
from app.utils.strings import ConstStrings

app = FastAPI()
# Handel Global Middleware
app.middleware("http")(app_middleware)
@app.get('/',tags=[ConstStrings.HEALTH_CHECK_ROUTE],summary=ConstStrings.HEALTH_CHECK_API)
def home():
    return   {
        "status": True,
        "statusCode": 200,
        "message": "API Works successfully!",
        "data": {}
    }

# CORS (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Include Routers
app.include_router(home_route.router) # home route
app.include_router(auth_routes.router) # auth route
app.include_router(user_routes.router) # user route
app.include_router(category_routes.router) # category routes
app.include_router(products_route.router) # products routes
app.mount("/media", StaticFiles(directory="media"), name="media") # product images
app.include_router(cart_route.router) # cart routes
app.include_router(wishlist_route.router) # wishlist routes
app.include_router(address_route.router) # address routes
app.include_router(order_route.router) # order routes
app.include_router(chatbot_route.router) # chatbot routes
app.include_router(notification_route.router) # notification routes
app.include_router(banners_route.router) # banners routes
Base.metadata.create_all(bind=engine)



# browser UI

admin = Admin(app, engine)

EXCLUDED_MODELS = []

for mapper in Base.registry.mappers:
    model_class = mapper.class_

    if model_class.__name__ in EXCLUDED_MODELS:
        continue

    columns = list(model_class.__table__.columns)

    class DynamicAdmin(ModelView, model=model_class):
        column_list = columns
        page_size = 50
        can_export = True

    admin.add_view(DynamicAdmin)