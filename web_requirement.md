ฉันได้สร้างโฟลเดอร์ website เพื่อเป็นระบบ จัดการสต็อค ที่ใช้ฐานข้อมูลและการทำงานเหมือนใน program desktop แต่จะมีบางอย่างที่ไม่เหมือนกับในระบบ program desktop

สิ่งที่ไม่เหมือนใน program desktop
- ในระบบ website จะเข้าสู่ระบบผ่าน username , password ที่มีการเข้ารหัส เพื่อความปลอดภัย อาจมีการใช้ jwt มาร่วมด้วย
- จะไม่มีการจัดการกับ database พวก migrate ต่างๆ มีแค่ query แสดงข้อมูล ลบ แก้ไข อัพเดท เท่านั้น

โครงสร้าง folder, file สำหรับการพัฒนา
- แบ่งไฟล์สำหรับจัดการหน้าต่างๆคร่าวๆดังนี้
website/
├── apps/
│   ├── api/               # สำหรับจัดการ api ต่างๆ
│   │   ├── product/
│   │   │   ├── route.ts
│   │   ├── stock/
│   │   │   ├── route.ts
│   │   ├── activity/
│   │   │   ├── route.ts
│   │   ├── user/
│   │   │   ├── route.ts
│   ├── views/               # สำหรับแสดงหน้าต่างๆ
│   │   ├── product/
│   │   │   ├── page.tsx
│   │   │   ├── style/
│   │   │   ├── components/
│   │   │   ├── ProductView.tsx
│   │   ├── stock/
│   │   │   ├── page.tsx
│   │   │   ├── style/
│   │   │   ├── components/
│   │   │   ├── StockView.tsx
│   │   ├── activity/
│   │   │   ├── page.tsx
│   │   │   ├── style/
│   │   │   ├── components/
│   │   │   ├── ActivityView.tsx
│   │   ├── dashboard/
│   │   │   ├── page.tsx
│   │   │   ├── style/
│   │   │   ├── components/
│   │   │   ├── DashboardView.tsx
│   │   ├── users/
│   │   │   ├── page.tsx
│   │   │   ├── style/
│   │   │   ├── components/
│   │   │   ├── UsersView.tsx
│   ├── models/            # model ต่างๆ
│   │   ├── User.ts
│   │   ├── Product.ts
│   │   ├── Stock.ts
│   │   ├── Activity.ts

ประสิทธิภาพการทำงานของโค้ด
- ทำงานได้อย่างรวดเร็ว
- query ข้อมูลได้อย่างมีประสิทธิภาพ

ux/ui ของระบบ
- ต้องกำหนด ui ให้เป็นทิศทางเดียวกัน
- ใช้ tailwind ได้
- ตัด animation ภาพเลื่อนไหวต่างๆ ยกเว้น loading
- menu ต่างๆอยู่ใน navbar ไม่มี sidebar
- รองรับการแสดงผลผ่าน มือถือ แท็บเล็ต
