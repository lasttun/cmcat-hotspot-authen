import pandas as pd

def prepare_firebase_users(input_excel, output_csv):
    print("กำลังอ่านข้อมูลจากไฟล์ Excel...")
    
    # อ่านไฟล์ Excel โดยข้าม 5 บรรทัดแรกที่เป็นหัวกระดาษของวิทยาลัย
    try:
        df = pd.read_excel(input_excel, sheet_name="Student List", header=5)
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")
        return

    # คัดเลือกเฉพาะคอลัมน์ที่จำเป็นต้องใช้
    cols = ['เลขประจำตัวประชาชน', 'รหัสประจำตัว', 'คำนำหน้าชื่อ', 'ชื่อ (ไทย)', 'นามสกุล (ไทย)']
    
    # ตัดแถวที่ไม่มีรหัสประจำตัวหรือเลขบัตรประชาชนออก
    df_sub = df[cols].dropna(subset=['รหัสประจำตัว', 'เลขประจำตัวประชาชน']).copy()

    # สร้าง DataFrame ใหม่สำหรับ Export
    df_export = pd.DataFrame()

    # 1. สร้าง email จำลอง (รหัสนักศึกษา@cmcat.local)
    df_export['email'] = df_sub['รหัสประจำตัว'].astype(str).str.split('.').str[0].str.strip() + '@cmcat.local'

    # 2. สร้าง password (รองรับทั้งเลขบัตร ปชช. 13 หลัก และรหัสเด็กหัว G)
    # อนุญาตให้เก็บเฉพาะตัวเลข (0-9) และตัวอักษรภาษาอังกฤษ (a-z, A-Z) ลบสัญลักษณ์พิเศษ/ขีด/ช่องว่างทิ้ง
    df_export['password'] = df_sub['เลขประจำตัวประชาชน'].astype(str).str.replace(r'[^0-9a-zA-Z]', '', regex=True).str.strip()

    # 3. สร้าง displayName (คำนำหน้า + ชื่อ + นามสกุล)
    df_export['displayName'] = (df_sub['คำนำหน้าชื่อ'].fillna('') + 
                                df_sub['ชื่อ (ไทย)'].fillna('') + ' ' + 
                                df_sub['นามสกุล (ไทย)'].fillna('')).str.strip()

    # ตรวจสอบความปลอดภัย: กรองเอาเฉพาะรายการที่รหัสผ่านมีความยาว 13 หลัก (รวมตัว G แล้ว)
    valid_mask = df_export['password'].str.len() == 13
    df_ready = df_export[valid_mask]
    
    invalid_count = len(df_export) - len(df_ready)

    # บันทึกเป็นไฟล์ CSV (เข้ารหัส utf-8-sig เพื่อรองรับภาษาไทย)
    df_ready.to_csv(output_csv, index=False, encoding='utf-8-sig')

    print("-" * 40)
    print(f"✅ ปรับปรุงและเตรียมข้อมูลสำเร็จ!")
    print(f"นำส่งข้อมูลผู้ใช้งานรวมทั้งสิ้น: {len(df_ready)} รายการ (รวมกลุ่มรหัสหัว G เรียบร้อย)")
    if invalid_count > 0:
        print(f"⚠️ ถูกตัดออกเนื่องจากความยาวไม่ครบ 13 หลักจริง ๆ: {invalid_count} รายการ")
    print(f"ไฟล์อัปเดตถูกบันทึกไว้ที่: {output_csv}")
    print("-" * 40)

# สั่งรันฟังก์ชัน
input_file = '20260703111426.xlsx' 
output_file = 'users_ready.csv'
prepare_firebase_users(input_file, output_file)