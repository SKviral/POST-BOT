# Telegram Link+Image Poster Bot (Vercel + Supabase)

## যেভাবে বটটি কাজ করে
1. তুমি বটে একটা লিংক পাঠাও
2. তারপর একটা ছবি পাঠাও
3. বট ছবিটা হেডার + লিংক + ফুটার সহ ক্যাপশন বানিয়ে, তোমার যোগ করা সব চ্যানেলে পোস্ট করে দেয়

## ধাপ ১ — Telegram বট তৈরি
1. Telegram এ `@BotFather` কে মেসেজ দাও, `/newbot` কমান্ড দিয়ে বট বানাও
2. যে টোকেন পাবে সেটা সেভ রাখো (`BOT_TOKEN`)
3. তোমার নিজের Telegram user ID বের করতে `@userinfobot` কে মেসেজ দাও (`ADMIN_ID`)

## ধাপ ২ — Supabase সেটআপ
1. https://supabase.com এ ফ্রি অ্যাকাউন্ট খোলো, নতুন প্রজেক্ট বানাও
2. প্রজেক্টের ভেতরে **SQL Editor** এ গিয়ে `supabase_schema.sql` ফাইলের কোড রান করো (এতে ৩টা টেবিল তৈরি হবে)
3. **Project Settings → API** থেকে নাও:
   - `Project URL` → এটা `SUPABASE_URL`
   - `service_role` key (secret) → এটা `SUPABASE_SERVICE_KEY`

   ⚠️ `service_role` key কখনো ফ্রন্টএন্ড/ক্লায়েন্ট কোডে ব্যবহার কোরো না — শুধু সার্ভার সাইডে (এখানে ঠিক আছে, কারণ এটা Vercel এর সার্ভারলেস ফাংশনে চলবে)

## ধাপ ৩ — Vercel এ ডিপ্লয়
1. এই পুরো ফোল্ডারটা একটা GitHub রিপোতে পুশ করো
2. https://vercel.com এ গিয়ে GitHub রিপো ইম্পোর্ট করো
3. Deploy করার আগে **Environment Variables** এ গিয়ে ৪টা ভ্যারিয়েবল যোগ করো (`.env.example` দেখো):
   - `BOT_TOKEN`
   - `ADMIN_ID`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
4. Deploy চাপো — কিছুক্ষণের মধ্যে একটা লিংক পাবে, যেমন: `https://tg-poster-bot.vercel.app`

## ধাপ ৪ — Telegram কে webhook URL বলে দাও
ব্রাউজারে এই লিংকটা ওপেন করো (নিজের টোকেন আর ভার্সেল URL বসিয়ে):

```
https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://your-project.vercel.app/api/webhook
```

`"ok":true` দেখলে বুঝবে সেটআপ সম্পন্ন।

## ধাপ ৫ — ব্যবহার শুরু
নিজের বটে `/start` পাঠাও। তারপর:
- `/addchannel -1001234567890` দিয়ে চ্যানেল যোগ করো (চ্যানেলের numeric ID — বটকে অবশ্যই সেই চ্যানেলে **admin** বানাতে হবে)
- `/setheader তোমার হেডার টেক্সট`
- `/setfooter তোমার ফুটার টেক্সট`
- এরপর লিংক পাঠাও, তারপর ছবি পাঠাও — বট বাকিটা করে দেবে

## চ্যানেলের numeric ID কীভাবে বের করবে
- চ্যানেলে যেকোনো একটা মেসেজ ফরওয়ার্ড করো `@userinfobot` বা `@JsonDumpBot` তে — সেখানে chat_id দেখতে পাবে (`-100` দিয়ে শুরু হবে)
- অথবা বটকে চ্যানেলের admin বানিয়ে একটা মেসেজ পাঠালে Supabase এ ম্যানুয়ালি insert করেও রাখা যায়

## খরচ
- Vercel ফ্রি টিয়ার: serverless function হওয়ায় idle সময়ে কোনো রিসোর্স খরচ হয় না
- Supabase ফ্রি টিয়ার: 500MB ডাটাবেজ, এই ছোট বটের জন্য যথেষ্টের চেয়ে বেশি
