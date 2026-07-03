const { initializeApp, cert } = require('firebase-admin/app');
const { getAuth } = require('firebase-admin/auth');
const fs = require('fs');
const csv = require('csv-parser');

const serviceAccount = require('./service-account.json');

initializeApp({
  credential: cert(serviceAccount)
});

const auth = getAuth();
const usersToImport = [];

console.log("🚀 กำลังอ่านไฟล์ users_ready.csv...");

fs.createReadStream('users_ready.csv')
  .pipe(csv({
    mapHeaders: ({ header }) => header.trim().replace(/^[\uFEFF\xA0]+|[\uFEFF\xA0]+$/g, '')
  }))
  .on('data', (row) => {
    if (!row.email) return;

    usersToImport.push({
      uid: String(row.email).split('@')[0], 
      email: String(row.email),
      password: String(row.password), // เปลี่ยนมาใช้ password ธรรมดาแทน passwordHash
      displayName: String(row.displayName)
    });
  })
  .on('end', async () => {
    console.log(`✅ พบรายชื่อนักศึกษาทั้งหมด: ${usersToImport.length} รายการ`);
    console.log("⏳ กำลังเริ่มทะลวงสร้างบัญชีทีละรายการ (อาจใช้เวลาประมาณ 1-2 นาที)...");

    let successCount = 0;
    let failureCount = 0;

    // วนลูปสร้างผู้ใช้งานทีละคน
    for (const user of usersToImport) {
      try {
        await auth.createUser({
          uid: user.uid,
          email: user.email,
          password: user.password,
          displayName: user.displayName,
        });
        successCount++;
        // พิมพ์จุดเพื่อบอกสถานะว่ากำลังทำงานอยู่
        process.stdout.write("."); 
      } catch (error) {
        // ถ้าระบบฟ้องว่ามีอีเมลนี้อยู่แล้ว ให้ทำการอัปเดตข้อมูลแทน
        if (error.code === 'auth/uid-already-exists' || error.code === 'auth/email-already-exists') {
          try {
            await auth.updateUser(user.uid, {
              password: user.password,
              displayName: user.displayName,
            });
            successCount++;
            process.stdout.write("+"); // เครื่องหมาย + คือการอัปเดต
          } catch (updateErr) {
            failureCount++;
            console.log(`\n⚠️ อัปเดต ${user.email} ไม่สำเร็จ: ${updateErr.message}`);
          }
        } else {
          failureCount++;
          console.log(`\n⚠️ สร้าง ${user.email} ไม่สำเร็จ: ${error.message}`);
        }
      }
    }

    console.log("\n-----------------------------------------");
    console.log(`🎉 สร้างและอัปเดตบัญชีสำเร็จ: ${successCount} คน`);
    if (failureCount > 0) {
      console.log(`⚠️ มีข้อผิดพลาดเกิดขึ้น: ${failureCount} คน`);
    }
    console.log("-----------------------------------------");
  });