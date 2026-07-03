import pandas as pd

# อ่านไฟล์ CSV ที่เราเตรียมไว้
df = pd.read_csv('users_ready.csv')

# สร้างไฟล์สคริปต์สำหรับนำเข้า MikroTik
with open('mikrotik_users.rsc', 'w', encoding='utf-8') as f:
    f.write('/ip hotspot user\n')
    for index, row in df.iterrows():
        # ดึงเฉพาะรหัสนักศึกษา และ รหัสผ่าน
        uid = str(row['email']).split('@')[0]
        pwd = str(row['password'])
        f.write(f'add name="{uid}" password="{pwd}" profile="default" server="all"\n')

print("✅ สร้างไฟล์ mikrotik_users.rsc สำเร็จ! นำไปลากวางใน MikroTik ได้เลย")