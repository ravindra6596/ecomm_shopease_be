from datetime import datetime


def format_datetime(dt):
    if not dt:
        return ""

    # If already string → return as is or parse it
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt  # fallback: return original string

    return dt.strftime("%d-%m-%Y %I:%M %p")


def build_order_email(order):
    # Delivery Address
    address = order.address

    address_html = f"""
    <div style="
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 16px;
    margin: 20px 0;
    background-color: #F9FAFB;
">
    <h3 style="margin-top: 0; color: #2563EB;">
        📍 Delivery Address
    </h3>

    <p style="margin: 0; line-height: 1.6;">
        {address.full_name}<br>
        {address.phone}<br>
        {address.address_line}<br>
        {address.city}, {address.state} - {address.pincode}
    </p>
</div>
    """

    items_html = ""

    for item in order.items:
        product_name = item.product.name
        qty = item.quantity
        price = item.price

        items_html += f"""
        <tr>
            <td>{product_name}</td>
            <td>{qty}</td>
            <td>₹{price}</td>
            <td>₹{qty * price}</td>
        </tr>
        """

    created_at = format_datetime(order.created_at)
    delivery_date = format_datetime(order.delivery_date)

    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">

            <h2 style="color:#2563EB;">
                Thank You for Your Order, {address.full_name}! 🛍️
            </h2>

            <p>
                We're delighted to confirm that your order has been placed successfully.
            </p>
            
            <p>
                Our team is preparing your items for shipment, and you'll receive further updates as your order progresses.
            </p>

            <p><b>Order ID:</b> #{order.id}</p>
            <p><b>Order Date:</b> {created_at}</p>
            <p><b>Status:</b> {(order.status or "").upper()}</p>
            <h3>🧾 Order Items</h3>

            <table border="1" cellpadding="8" cellspacing="0">
                <tr style="background:#f2f2f2;">
                    <th>Product</th>
                    <th>Qty</th>
                    <th>Price</th>
                    <th>Total</th>
                </tr>
                {items_html}
            </table>

            <h3>💰 Total Amount: ₹{order.total_amount}</h3>

            <p>🚚 <b>Expected Delivery:</b> {delivery_date}</p>

           {address_html}

            <h3 style="color:green;">🙏 Thank You for Shopping with Us!</h3>

            <p>
                We truly appreciate your order.<br>
                Our team is working hard to deliver your products safely and on time.
            </p>

            <p>
                If you have any questions, feel free to contact our support team.
            </p>

            <br>

            <p style="color:#2563EB;">
                — Team ShopEase ❤️
            </p>

        </body>
    </html>
    """

    return html
