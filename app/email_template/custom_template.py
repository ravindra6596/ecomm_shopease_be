from datetime import datetime
from babel.numbers import format_decimal

from app.utils.url_helper import build_image_url


def format_price(amount):
    if amount is None:
        return "0"

    return f"₹{format_decimal(amount,format='#,##,##0.0', locale='en_IN')}"
def format_datetime(dt):
    if not dt:
        return ""

    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt

    return dt.strftime("%d-%m-%Y")

def get_first_image(product):
    if product.images:
        return build_image_url(product.images[0].image_url)
    return ""
def build_order_block(order):
    if not order:
        return ""

    items_html = ""

    for item in order.items:
        print('Image URL',get_first_image(item.product))
        items_html += f"""
        <div style="
            border:1px solid #e5e7eb;
            border-radius:12px;
            padding:15px;
            margin-bottom:15px;
            background:#ffffff;
        ">

            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>

                    <!-- Product Image -->
                    <td width="90" valign="top">
                        <img
                            src="{get_first_image(item.product)}"
                            width="80"
                            height="80"
                            style="
                                border-radius:10px;
                                object-fit:cover;
                                border:1px solid #e5e7eb;
                            "
                        >
                    </td>

                    <!-- Product Details -->
                    <td valign="top">

                        <h3 style="
                            margin:0 0 8px 0;
                            color:#111827;
                            font-size:16px;
                        ">
                            {item.product.name}
                        </h3>

                        <p style="
                            margin:0 0 8px 0;
                            color:#6b7280;
                            font-size:14px;
                        ">
                            Quantity: {item.quantity}
                        </p>

                        <div style="margin-bottom:8px;">

                            <span style="
                                color:#9ca3af;
                                text-decoration:line-through;
                                font-size:14px;
                            ">
                                {format_price(item.price)}
                            </span>

                            <span style="
                                margin-left:8px;
                                color:#111827;
                                font-size:16px;
                                font-weight:bold;
                            ">
                                {format_price(item.product.discount_price)}
                            </span>

                        </div>

                        <span style="
                            background:#dcfce7;
                            color:#15803d;
                            padding:4px 8px;
                            border-radius:20px;
                            font-size:12px;
                            font-weight:bold;
                        ">
                            SAVE {format_price(item.price - item.product.discount_price)}
                        </span>

                        <p style="
                            margin-top:10px;
                            color:#16a34a;
                            font-size:15px;
                            font-weight:bold;
                        ">
                            Total: {format_price(item.quantity * item.product.discount_price)}
                        </p>

                    </td>

                </tr>
            </table>

        </div>
        """
    saved_amount = (
            order.total_amount -
            order.total_discount_price
    )
    summary_html = f"""
    <div style="
        background:#ffffff;
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:15px;
        margin-top:15px;
    ">

        <table width="100%">
            <tr>
                <td>Subtotal</td>
                <td align="right">
                    {format_price(order.total_amount)}
                </td>
            </tr>
             <tr>
                <td>
                    Total Discount
                </td>
                <td align="right">
                    {format_price(order.total_amount - order.total_discount_price)}
                </td>
            </tr>
            <tr>
                <td>Shipping Charges</td>
                <td align="right">
                    {format_price(order.shipping)}
                </td>
            </tr>

            <tr>
                <td style="color:#16a34a;font-weight:bold;">
                    Total Saving
                </td>
                <td align="right"
                    style="color:#16a34a;font-weight:bold;">
                    {format_price(saved_amount - order.shipping)}
                </td>
            </tr>

        </table>

    </div>
    """

    grand_total_html = f"""
    <div style="
        background:#f0fdf4;
        border:2px solid #bbf7d0;
        border-radius:12px;
        padding:20px;
        margin-top:20px;
    ">

        <table width="100%">
            <tr>
                <td style="
                    font-size:15px;
                    font-weight:bold;
                    color:#166534;
                ">
                    Grand Total
                </td>

                <td align="right" style="
                    font-size:18px;
                    font-weight:bold;
                    color:#16a34a;
                ">
                    {format_price(order.total_discount_price + order.shipping)}
                </td>
            </tr>
        </table>

    </div>
    """

    address = order.address
    created_at = format_datetime(order.created_at)
    delivery_date = format_datetime(order.delivery_date)
    if order.status.lower() == "delivered":
        delivery_html = """
        <p style="color:#16a34a;font-weight:bold;">
            🎉 <b>Delivered Successfully</b>
        </p>
        """
    else:
        delivery_html = f"""
        <p>🚚 <b>Expected Delivery:</b> {delivery_date}</p>
        """
    return f"""
    <div style="background:#F9FAFB;padding:15px;border-radius:10px;margin-top:20px;">

        <h3>📦 Order Details</h3>

        <p><b>Order ID:</b> #{order.id}</p>
        <p><b>Status:</b> {order.status.upper()}</p>
        <h3>💰 Total Amount: {format_price(order.total_discount_price + order.shipping)}</h3>
        <p>🗓 <b>Order Date:</b> {created_at}</p>
        {delivery_html}
        <h3>🧾 Items</h3>
        
            {items_html}
            
            {summary_html}
            
            {grand_total_html}

        <h3>📍 Delivery Address</h3>

        <p>
            {address.full_name}<br>
            {address.phone}<br>
            {address.address_line}<br>
            {address.city}, {address.state} - {address.pincode}
        </p>
        
    </div>
    """


EMAIL_CONFIG = {
    "signup": {
        "title": "🎉 Welcome to ShopEase",
        "message": "Your account has been created successfully. Start shopping now!",
        "color": "#2563EB",
        "cta": "Start Shopping",
        "subject": "Welcome to ShopEase 🎉",
        "show_order": False,
        "footer1": "🛍️ Welcome to the ShopEase Family!",
        "footer2": "We're excited to have you with us and look forward to providing you with a seamless shopping experience.",
        "footer3": "Start exploring our products and enjoy exclusive offers designed just for you."
    },

    "order_placed": {
        "title": "🛒 Order Confirmed",
        "message": "Your order has been placed successfully. We’ve received it and our team is now preparing your items for shipment. You’ll receive updates as your order progresses.",
        "color": "#2563EB",
        "cta": "View Order",
        "subject": "Your Order is Confirmed 🛒",
        "show_order": True,
        "footer1": "🙏 Thank You for Shopping with Us!",
        "footer2": "We truly appreciate your order. Our team is working hard to prepare and dispatch your items as quickly as possible.",
        "footer3": "If you have any questions or need assistance, please don't hesitate to contact us."
    },

    "shipped": {
        "title": "🚚 Order Shipped",
        "message": "Great news! Your order has been shipped and is on its way to you.",
        "color": "#0EA5E9",
        "cta": "Track Order",
        "subject": "Your Order Has Been Shipped 🚚",
        "show_order": True,
        "footer1": "📦 Your Package Is On The Way!",
        "footer2": "Our delivery partners are working to get your order to you safely and on time.",
        "footer3": "You can track your shipment anytime using the tracking information provided."
    },

    "out_for_delivery": {
        "title": "📦 Out for Delivery",
        "message": "Your order is out for delivery and should arrive today.",
        "color": "#F59E0B",
        "cta": "Track Delivery",
        "subject": "Out for Delivery 📦",
        "show_order": True,
        "footer1": "🚪 Get Ready, Your Order Is Almost Here!",
        "footer2": "Our delivery partner is on the way with your package and will attempt delivery shortly.",
        "footer3": "Please ensure someone is available at the delivery address to receive the order."
    },

    "delivered": {
        "title": "🎉 Delivered Successfully",
        "message": "Your order has been delivered successfully. We hope you love your purchase!",
        "color": "#10B981",
        "cta": "Rate Order",
        "subject": "Delivered Successfully 🎉",
        "show_order": True,
        "footer1": "❤️ Thank You For Choosing ShopEase!",
        "footer2": "We hope your shopping experience was smooth and enjoyable from start to finish.",
        "footer3": "We'd love to hear your feedback. Your review helps us serve you better."
    },

    "cancelled": {
        "title": "❌ Order Cancelled",
        "message": "Your order has been cancelled. Any applicable refund will be processed according to our refund policy.",
        "color": "#EF4444",
        "cta": "Contact Support",
        "subject": "Order Cancelled ❌",
        "show_order": True,
        "footer1": "📋 Cancellation Confirmed",
        "footer2": "We're sorry that this order could not be completed. Any eligible refund will be processed as soon as possible.",
        "footer3": "If you need assistance or would like to place a new order, our support team is here to help."
    }
}


def build_email(user_name, email_type, order=None):
    config = EMAIL_CONFIG[email_type]

    order_block = build_order_block(order) if config["show_order"] else ""

    html = f"""
    <html>
    <body style="margin:0;background:#f5f7fb;font-family:Arial;">

        <div style="max-width:650px;margin:30px auto;background:white;border-radius:10px;overflow:hidden;">

            <!-- HEADER -->
            <div style="background:{config['color']};padding:25px;text-align:center;color:white;">
                <h1 style="margin:0;">ShopEase</h1>
            </div>

            <!-- BODY -->
            <div style="padding:25px;">

                <h2>{config['title']}</h2>

                <p>Hi {user_name},</p>

                <p>{config['message']}</p>

                {order_block}

                <!-- CTA -->
                <div style="text-align:center;margin-top:25px;">
                    <a href="https://your-app.com"
                       style="background:{config['color']};
                              color:white;
                              padding:12px 24px;
                              text-decoration:none;
                              border-radius:8px;
                              display:inline-block;">
                        {config['cta']}
                    </a>
                </div>

                <hr>
                <!-- FOOTER -->
                <h3 style="color:green;">{config['footer1']}</h3>

            <p>{config['footer2']}</p>

            <p>{config['footer3']} </p>
                <p style="text-align:center;font-size:12px;color:#777;">
                    Need help? support.shopease@gmail.com
                </p>

                <p style="text-align:center;color:{config['color']}">
                    — Team ShopEase ❤️
                </p>

            </div>

        </div>

    </body>
    </html>
    """

    return config["subject"], html
