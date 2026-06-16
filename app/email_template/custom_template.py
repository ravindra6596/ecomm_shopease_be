from datetime import datetime


def format_datetime(dt):
    if not dt:
        return ""

    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt

    return dt.strftime("%d-%m-%Y %I:%M %p")

def build_order_block(order):
    if not order:
        return ""

    items_html = ""

    for item in order.items:
        items_html += f"""
        <tr>
            <td>{item.product.name}</td>
            <td>{item.quantity}</td>
            <td>₹{item.price}</td>
            <td>₹{item.quantity * item.price}</td>
        </tr>
        """

    address = order.address
    created_at = format_datetime(order.created_at)
    delivery_date = format_datetime(order.delivery_date)
    return f"""
    <div style="background:#F9FAFB;padding:15px;border-radius:10px;margin-top:20px;">

        <h3>📦 Order Details</h3>

        <p><b>Order ID:</b> #{order.id}</p>
        <p><b>Status:</b> {order.status.upper()}</p>
        <h3>💰 Total Amount: ₹{order.total_amount}</h3>
        <p>🗓 <b>Order Date:</b> {created_at}</p>
        <p>🚚 <b>Expected Delivery:</b> {delivery_date}</p>
        <h3>🧾 Items</h3>

        <table width="100%" border="1" cellpadding="8" cellspacing="0">
            <tr style="background:#f3f4f6;">
                <th>Product</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Total</th>
            </tr>
            {items_html}
        </table>

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