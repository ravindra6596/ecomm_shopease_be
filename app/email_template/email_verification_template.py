SUCCESS_HTML = """
<!DOCTYPE html>
<html>

<head>
    <title>Email Verified</title>
</head>

<body style="margin:0;background:#f5f7fb;font-family:Arial">

    <div style="max-width:500px;margin:80px auto;background:#fff;padding:40px;border-radius:16px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,.08)">

        <div style="font-size:70px">✅</div>

        <h1 style="color:#22c55e">
            Email Verified
        </h1>

        <p style="color:#666">
            Your email has been verified successfully.
        </p>

        <p style="color:#666">
            You can now login to your account.
        </p>

    </div>

</body>

</html>
"""

ALREADY_VERIFIED_HTML = """
<!DOCTYPE html>
<html>

<head>
    <title>Already Verified</title>
</head>

<body style="margin:0;background:#f5f7fb;font-family:Arial">

    <div style="max-width:500px;margin:80px auto;background:#fff;padding:40px;border-radius:16px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,.08)">

        <div style="font-size:70px">ℹ️</div>

        <h1 style="color:#2563eb">
            Already Verified
        </h1>

        <p style="color:#666">
            Your email has already been verified.
        </p>

        <p style="color:#666">
            You can login to your account.
        </p>

    </div>

</body>

</html>
"""

INVALID_HTML = """
<!DOCTYPE html>
<html>

<head>
    <title>Invalid Link</title>
</head>

<body style="margin:0;background:#f5f7fb;font-family:Arial">

    <div style="max-width:500px;margin:80px auto;background:#fff;padding:40px;border-radius:16px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,.08)">

        <div style="font-size:70px">❌</div>

        <h1 style="color:#ef4444">
            Invalid Link
        </h1>

        <p style="color:#666">
            This verification link is invalid or has expired.
        </p>

        <p style="color:#666">
            Please request a new verification email.
        </p>

    </div>

</body>

</html>
"""
EMAIL_VERIFY_TEMPLATE = """
<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>Verify Email</title>
</head>

<body style="
    margin:0;
    padding:0;
    background:#f5f7fb;
    font-family:Arial,sans-serif;
">

    <div style="
    max-width:600px;
    margin:40px auto;
    background:#ffffff;
    border-radius:16px;
    padding:40px;
    text-align:center;
    box-shadow:0 4px 20px rgba(0,0,0,.08);
">
         <h1 style="
        color:#2563eb;
        margin-bottom:20px;
    ">
            Hello <b>{name},</b>
        </h1>
        
        <h1 style="
        color:#2563eb;
        margin-bottom:20px;
    ">
            Welcome to ShopEase 🎉
        </h1>

        <p style="
        color:#555;
        font-size:16px;
        line-height:1.6;
    ">
            Thank you for creating an account.
        </p>

        <p style="
        color:#555;
        font-size:16px;
        line-height:1.6;
    ">
            Please verify your email address by clicking the button below.
        </p>

        <a href="{verification_link}" style="
            display:inline-block;
            margin-top:20px;
            background:#2563eb;
            color:white;
            text-decoration:none;
            padding:14px 32px;
            border-radius:8px;
            font-size:16px;
            font-weight:bold;
       ">
            Verify Email
        </a>

        <p style="
        margin-top:30px;
        color:#888;
        font-size:14px;
    ">
            If the button doesn't work, copy and paste this link into your browser:
        </p>

        <p style="
        color:#2563eb;
        font-size:13px;
        word-break:break-all;
    ">
            {verification_link}
        </p>

        <hr style="
        border:none;
        border-top:1px solid #eee;
        margin:30px 0;
    ">

        <p style="
        color:#999;
        font-size:12px;
    ">
            This verification link is intended for your account only.
        </p>

    </div>

</body>

</html>
"""
