from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle

def generate_order_invoice(order):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        leftMargin=25,
        rightMargin=25,
        topMargin=25,
        bottomMargin=25,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]

    right_style = ParagraphStyle(
        "right",
        parent=styles["Normal"],
        alignment=TA_RIGHT,
    )
    logo = Image(
        "app/assets/shopease_logo.png",
        width=80,
        height=80
    )
    company_info = Paragraph(
        """
        <b>ShopEase</b><br/>
        GSTIN: 27ABCDE1234F1Z5<br/>
        support@shopease.com<br/>
        +91 9876543210
        """,
        styles["BodyText"]
    )

    left_section = Table(
        [[logo, company_info]],
        colWidths=[60, 220]
    )

    left_section.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (1, 0), (1, 0), 10),
        ])
    )

    left_section.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ])
    )
    elements = []

    # ==================================================
    # HEADER
    # ==================================================

    header_data = [
        [
            left_section,
            Paragraph(
                "<b>TAX INVOICE</b>",
                right_style,
            ),
        ]
    ]

    header = Table(
        header_data,
        colWidths=[300, 220],
    )

    header.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 1, colors.white),
            ("PADDING", (0, 0), (-1, -1), 10),
        ])
    )

    elements.append(header)
    elements.append(Spacer(1, 15))

    # ==================================================
    # INVOICE DETAILS
    # ==================================================

    invoice_data = [
        [
            Paragraph(
                f"""
                <b>Invoice No:</b> INV-{order.id}<br/>
                <b>Invoice Date:</b> {order.created_at.strftime('%d-%m-%Y')}
                """,
                styles["Normal"],
            ),
            Paragraph(
                f"""
                <b>Order No:</b> {order.id}<br/>
                <b>Order Date:</b> {order.created_at.strftime('%d-%m-%Y')}
                """,
                styles["Normal"],
            ),
        ]
    ]

    invoice_table = Table(
        invoice_data,
        colWidths=[260, 260],
    )

    invoice_table.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )

    elements.append(invoice_table)
    elements.append(Spacer(1, 15))

    # ==================================================
    # ADDRESS SECTION
    # ==================================================

    address = order.address

    address_table = Table(
        [
            [
                Paragraph(
                    f"""
                    <b>BILLING ADDRESS</b><br/><br/>
                    {address.full_name}<br/>
                    {address.address_line}<br/>
                    {address.city}, {address.state}<br/>
                    {address.country} - {address.pincode}<br/>
                    Phone: {address.phone}
                    """,
                    styles["Normal"],
                ),
                Paragraph(
                    f"""
                    <b>SHIPPING ADDRESS</b><br/><br/>
                    {address.full_name}<br/>
                    {address.address_line}<br/>
                    {address.city}, {address.state}<br/>
                    {address.country} - {address.pincode}<br/>
                    Phone: {address.phone}
                    """,
                    styles["Normal"],
                ),
            ]
        ],
        colWidths=[260, 260],
    )

    address_table.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )

    elements.append(address_table)
    elements.append(Spacer(1, 15))

    # ==================================================
    # PRODUCT TABLE
    # ==================================================

    product_data = [
        [
            "Product",
            "Qty",
            "Price",
            "Total",
        ]
    ]

    for item in order.items:
        product_data.append(
            [
                Paragraph(
                    item.product.name,
                    styles["BodyText"]
                ),
                str(item.quantity),
                f"{item.price:,.2f}",
                f"{(item.quantity * item.price):,.2f}",
            ]
        )

    product_table = Table(
        product_data,
        colWidths=[290, 60, 85, 85],
    )

    product_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2874F0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

            ("ALIGN", (1, 1), (-1, -1), "CENTER"),

            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ])
    )

    elements.append(product_table)
    elements.append(Spacer(1, 20))

    # ==================================================
    # TOTALS
    # ==================================================

    subtotal = order.total_amount
    shipping = 0
    discount = 0
    grand_total = subtotal

    totals_table = Table(
        [
            ["Subtotal", f"{subtotal:,.2f}"],
            ["Shipping", f"{shipping:,.2f}"],
            ["Discount", f"{discount:,.2f}"],
            ["Grand Total", f"RS. {grand_total:,.2f}"],
        ],
        colWidths=[120, 120],
    )

    totals_table.hAlign = "RIGHT"

    totals_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

            ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#E8F0FE")),

            ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
        ])
    )

    elements.append(totals_table)
    elements.append(Spacer(1, 20))

    # ==================================================
    # PAYMENT DETAILS
    # ==================================================

    elements.append(
        Paragraph(
            f"<b>Payment Method:</b> {order.payment_method.upper()}",
            styles["Normal"],
        )
    )

    elements.append(
        Paragraph(
            f"<b>Payment Status:</b> {order.payment_status.upper()}",
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 20))

    # ==================================================
    # FOOTER
    # ==================================================

    elements.append(
        Paragraph(
            "Thank you for shopping with us!",
            styles["Heading3"],
        )
    )

    doc.build(elements)

    buffer.seek(0)

    return buffer