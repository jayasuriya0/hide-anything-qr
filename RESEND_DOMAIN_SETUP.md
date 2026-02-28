# Verify Domain in Resend - Step-by-Step Guide

## ✅ Current Status
- Email system is **working perfectly!** ✅
- Successfully sent test email to your own address (suriyaganesh301@gmail.com)
- Resend API key configured correctly
- Code is production-ready

## 🎯 Goal
Verify a custom domain so you can send emails to **any recipient** (not just yourself).

---

## 📋 Prerequisites

You need **one of these**:
1. **Your own domain** (e.g., hideqr.app, mycoolapp.com)
2. **A free domain** from providers like:
   - Freenom (free .tk, .ml domains)
   - Netlify (free subdomain: yourapp.netlify.app)
   - Vercel (free subdomain: yourapp.vercel.app)

**Don't have a domain?** Skip to "Alternative: Use Subdomain" section below.

---

## 🚀 Step 1: Add Domain to Resend

### 1.1 Go to Resend Dashboard
Visit: https://resend.com/domains

### 1.2 Click "Add Domain"
Click the **"Add Domain"** button

### 1.3 Enter Your Domain
Examples:
- If you own `hideqr.app` → Enter: `hideqr.app`
- If using subdomain → Enter: `mail.hideqr.app` or `app.hideqr.app`

### 1.4 Choose Region
Select: **United States (US)** (or your preferred region)

Click **"Add"**

---

## 🔧 Step 2: Add DNS Records

Resend will show you **3 DNS records** to add:

### Record 1: SPF (TXT Record)
```
Type: TXT
Name: @ (or your domain)
Value: v=spf1 include:resend.com ~all
```

### Record 2: DKIM (TXT Record)
```
Type: TXT
Name: resend._domainkey
Value: [long string provided by Resend]
```

### Record 3: DMARC (TXT Record) - Optional but recommended
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=none
```

### Where to Add DNS Records?

Go to your domain provider's DNS settings:
- **Namecheap**: Advanced DNS tab
- **GoDaddy**: DNS Management
- **Cloudflare**: DNS tab
- **Google Domains**: DNS settings
- **Netlify/Vercel**: DNS/Domain settings

---

## ⏰ Step 3: Wait for Verification

- DNS propagation takes **5 minutes to 48 hours** (usually 15-30 minutes)
- Resend will automatically verify your domain
- Check verification status at: https://resend.com/domains

**Tip**: Use https://mxtoolbox.com/SuperTool.aspx to check if DNS records are live

---

## 🎯 Step 4: Update Render Environment Variable

Once your domain is **verified** in Resend:

### 4.1 Go to Render Dashboard
https://dashboard.render.com

### 4.2 Select Your Service
Click: **hide-anything-qr**

### 4.3 Go to Environment Tab
Click **"Environment"** in left sidebar

### 4.4 Update RESEND_FROM_EMAIL
Find the `RESEND_FROM_EMAIL` variable and change it to:

```
RESEND_FROM_EMAIL=noreply@yourdomain.com
```

**Examples**:
- `noreply@hideqr.app`
- `hello@hideqr.app`
- `qr@hideqr.app`
- `notifications@hideqr.app`

**Important**: Use an email address **@yourdomain.com** (the domain you verified)

### 4.5 Save Changes
Click **"Save Changes"** - Render will redeploy automatically

---

## ✅ Step 5: Test Sending to Any Email

After Render redeploys (~2 minutes):

1. Go to your app: https://hide-anything-qr.onrender.com
2. Share content with **any friend** (any email address)
3. Click **"Send via Email"**
4. Email will arrive to any recipient! 🎉

---

## 🆓 Alternative: Use Free Subdomain (If You Don't Own a Domain)

### Option A: Deploy Frontend to Netlify/Vercel

1. Deploy your frontend to **Netlify** or **Vercel** (free)
2. You'll get a subdomain: `hide-qr.netlify.app`
3. Verify this subdomain in Resend
4. Use emails like: `noreply@hide-qr.netlify.app`

### Option B: Use Gmail as Sender (Simple)

If you don't want to deal with domains:

1. In Resend, add and verify your Gmail: `suriyaganesh301@gmail.com`
2. Resend will send a verification email
3. Click the link to verify
4. Update Render:
   ```
   RESEND_FROM_EMAIL=suriyaganesh301@gmail.com
   ```
5. This way emails will come from your Gmail address!

**Note**: This requires email verification but works immediately.

---

## 🔍 Troubleshooting

### "Domain not verified after 1 hour"

Check DNS records:
1. Go to https://mxtoolbox.com/SuperTool.aspx
2. Enter: `resend._domainkey.yourdomain.com`
3. Select "TXT Lookup"
4. Verify the DKIM record appears correctly

### "Emails still not sending to others"

1. Check Resend dashboard: https://resend.com/domains
2. Verify domain shows **green checkmark** ✅
3. Confirm `RESEND_FROM_EMAIL` matches verified domain
4. Check Render logs for errors

### "I don't have access to DNS settings"

Options:
- Ask domain administrator for access
- Use Gmail verification method (Option B above)
- Switch to Mailgun (easier, no domain verification needed for sandbox)

---

## 📊 Current Configuration

**Working Configuration**:
```
RESEND_API_KEY=re_5iLuTX4a_C3Bq5op7CTy4RZWw7o1pfBqf
RESEND_FROM_EMAIL=onboarding@resend.dev (test only - your email only)
```

**After Domain Verification**:
```
RESEND_API_KEY=re_5iLuTX4a_C3Bq5op7CTy4RZWw7o1pfBqf
RESEND_FROM_EMAIL=noreply@yourdomain.com (send to anyone!)
```

---

## 📧 Example Email Addresses

Popular choices for sender addresses:
- `noreply@yourdomain.com` (most common)
- `hello@yourdomain.com` (friendly)
- `notifications@yourdomain.com` (descriptive)
- `qr@yourdomain.com` (app-specific)
- `team@yourdomain.com` (professional)

**Tip**: Use `noreply@` if you don't want users replying to emails.

---

## ✅ Summary

**Steps to Complete**:
1. ☐ Choose/buy a domain (or use free option)
2. ☐ Add domain to Resend: https://resend.com/domains
3. ☐ Add DNS records at domain provider
4. ☐ Wait for verification (15-30 mins)
5. ☐ Update `RESEND_FROM_EMAIL` in Render
6. ☐ Test sending to any email address!

---

## 🆘 Need Help?

If you:
- Don't have a domain
- Can't access DNS settings
- Want a faster solution

Let me know and I can:
1. Help you get a free domain/subdomain
2. Switch to Mailgun (works without domain verification)
3. Guide you through Gmail verification method

---

**Questions? Let me know what domain you have (or if you need help getting one)!**
