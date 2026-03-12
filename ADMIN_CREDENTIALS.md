# Admin Credentials for KR-CLIDN Development

## 🔐 DEFAULT ADMIN CREDENTIALS

```
Email:     admin@kr-clidn.local
Password:  KaliRoot@2026!Admin
```

## 📍 Access Admin Panel

1. Go to: `http://localhost:8000/admin/`
2. Login with credentials above
3. You'll access: `panel-plus.html` with all management features

## ⚙️ How to Set Up in Supabase

### Step 1: Create Admin User in Supabase
```sql
-- Log in to Supabase Dashboard
-- SQL Editor → Run query:

INSERT INTO auth.users (
  instance_id,
  id,
  aud,
  role,
  email,
  encrypted_password,
  email_confirmed_at,
  created_at,
  updated_at
) VALUES (
  '00000000-0000-0000-0000-000000000000',
  '00000000-0000-0000-0000-000000000001',
  'authenticated',
  'authenticated',
  'admin@kr-clidn.local',
  crypt('KaliRoot@2026!Admin', gen_salt('bf')),
  NOW(),
  NOW(),
  NOW()
);
```

### Step 2: Create Admin Profile Entry
```sql
INSERT INTO public.profiles (
  id,
  username,
  email,
  is_admin,
  created_at
) VALUES (
  '00000000-0000-0000-0000-000000000001',
  'admin',
  'admin@kr-clidn.local',
  true,
  NOW()
);
```

## 🔑 Alternative: Quick Access (Development Only)

If you want instant access without Supabase setup, you can temporarily bypass auth:

1. Open `/admin/panel-plus.html` directly in browser
2. The page is fully functional without login (for local development)
3. All management features work with localStorage

## ✅ Once You Have Access

**Login credentials remember:**
- Email: `admin@kr-clidn.local`
- Pass: `KaliRoot@2026!Admin`

**Then you can:**
- ✅ Configure installer download links
- ✅ Monitor web-cli synchronization
- ✅ View sales funnel analytics
- ✅ Manage packages and campaigns
- ✅ Export sync configuration

## 📌 For Production

**DO NOT use default credentials in production!**

Instead:
1. Generate strong admin password
2. Store securely in Supabase
3. Use environment variables for secrets
4. Enable 2FA in Supabase settings

---

**Note:** These are development-only credentials. Change immediately before deployment.
