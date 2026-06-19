import os
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
font_path = os.path.join(BASE_DIR, "assets", "GoogleSans-Medium.ttf")
pdfmetrics.registerFont(TTFont("GoogleSans", font_path))

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

    for s in styles.byName.values():
        s.fontName = "GoogleSans"

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
    company_style = ParagraphStyle(
        "company",
        fontName="GoogleSans",
        fontSize=10,
        leading=14,
    )

    company_info = Paragraph(
        """
        <b>ShopEase</b><br/>
        GSTIN: 27ABCDE1234F1Z5<br/>
        support@shopease.com<br/>
        +91 9876543210
        """,
        company_style
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
    normal_style = ParagraphStyle(
        "normal",
        fontName="GoogleSans",
        fontSize=10,
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
            "Product (₹)",
            "Qty (₹)",
            "Price (₹)",
            "Selling Price (₹)",
            "Total (₹)",
        ]
    ]

    green_style = ParagraphStyle(
        "green_price",
        parent=styles["BodyText"],
        textColor=colors.green,
        alignment=TA_CENTER,
    )
    discount_green_style = ParagraphStyle(
        "discount_green_style",
        parent=styles["BodyText"],
        textColor=colors.green,
    )

    for item in order.items:
        product_data.append(
            [
                Paragraph(
                    item.product.name,
                    styles["BodyText"]
                ),
                str(item.quantity),
                f"{item.price:,.2f}",
                Paragraph(
            f"<b>{item.product.discount_price:,.2f}</b>",
                    green_style,
                ),
                f"{(item.quantity * item.product.discount_price):,.2f}",
            ]
        )

    product_table = Table(
        product_data,
        colWidths=[210, 60, 85, 85],

    )

    table_style = [
        ("FONTNAME", (0, 0), (-1, -1), "GoogleSans"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2874F0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "GoogleSans"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DADADA")),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]

    for row in range(1, len(product_data)):
        if row % 2 == 0:
            table_style.append(
                ("BACKGROUND", (0, row), (-1, row), colors.HexColor("#F8F9FA"))
            )

    product_table.setStyle(TableStyle(table_style))

    elements.append(product_table)
    elements.append(Spacer(1, 20))

    # ==================================================
    # TOTALS
    # ==================================================

    subtotal = order.total_amount
    discounted_total = order.total_discount_price
    discount = round(subtotal - discounted_total)
    shipping = order.shipping
    grand_total = round(discounted_total + shipping)

    totals_table = Table(
        [
            [
                Paragraph("Subtotal", styles["Normal"]),
                Paragraph(f"{subtotal:,.2f}", styles["Normal"]),
            ],
            [
                Paragraph("Discount", styles["Normal"]),
                Paragraph(f"<b>{discount:,.2f}</b>", discount_green_style),
            ],
            [
                Paragraph("Protect Promise Fee", styles["Normal"]),
                Paragraph(f"{shipping:,.2f}", styles["Normal"]),
            ],
            [
                Paragraph("Grand Total", styles["Normal"]),
                Paragraph(f"₹ {grand_total:,.2f}", styles["Normal"]),
            ],
        ],
        colWidths=[120, 120],
    )

    totals_table.hAlign = "RIGHT"

    totals_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

            ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#E8F0FE")),

            ("FONTNAME", (0, 3), (-1, 3), "GoogleSans"),
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