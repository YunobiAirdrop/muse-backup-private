from pathlib import Path
import base64

root = Path('/home/hatch/workspace/your_files/cv-m-abdul-aziez')
img = root / '.src/media/profile.jpg'
photo = base64.b64encode(img.read_bytes()).decode('ascii')
html = r'''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CV M. Abdul Aziez</title>
<style>
@page { size: A4; margin: 0; }
* { box-sizing: border-box; print-color-adjust: exact; -webkit-print-color-adjust: exact; }
html, body { margin: 0; padding: 0; background: #e9e9e9; }
body { font-family: 'Noto Sans', 'Liberation Sans', sans-serif; color: #202226; }
.page { width: 210mm; height: 297mm; min-height: 297mm; background: #fff; padding: 10mm 16mm 11mm; position: relative; overflow: hidden; }
.header { display: grid; grid-template-columns: 25mm 1fr; gap: 7mm; align-items: center; padding-bottom: 3mm; border-bottom: 1.2mm solid #9d1320; }
.photo { width: 23mm; height: 28mm; object-fit: cover; object-position: 50% 34%; border-radius: 2mm; border: 0.7mm solid #9d1320; }
.name { margin: 0 0 1.5mm; font-size: 22pt; line-height: 1.02; letter-spacing: -0.5pt; color: #17191d; font-weight: 700; }
.role { margin: 0 0 3.2mm; color: #9d1320; font-size: 10.8pt; font-weight: 700; letter-spacing: 0.2pt; }
.contact { display: flex; flex-wrap: wrap; gap: 1.2mm 4.5mm; font-size: 9.4pt; line-height: 1.35; color: #454950; }
.contact a { color: #454950; text-decoration: none; }
.summary { margin: 2mm 0 1.8mm; padding: 2mm 3.5mm; background: #f5f2f2; border-left: 1.3mm solid #9d1320; font-size: 10pt; line-height: 1.38; }
.summary p { margin: 0; }
.content { display: block; }
.compact { margin: 0 0 1mm; font-size: 10pt; line-height: 1.3; }
section { break-inside: avoid; page-break-inside: avoid; display: flow-root; margin: 0 0 1mm; }
h2 { margin: 0 0 0.8mm; padding-bottom: 0.7mm; border-bottom: 0.45mm solid #cfd1d4; font-size: 10.2pt; line-height: 1.2; text-transform: uppercase; letter-spacing: 1.1pt; color: #9d1320; }
.skill-list { list-style: none; margin: 0; padding: 0; }
.skill-list li { margin: 0 0 1.8mm; padding-left: 3.8mm; position: relative; font-size: 10pt; line-height: 1.3; }
.skill-list li::before { content: ''; width: 1.4mm; height: 1.4mm; background: #9d1320; border-radius: 50%; position: absolute; left: 0; top: 1.5mm; }
.stack { font-size: 9.1pt; line-height: 1.48; color: #36393e; }
.stack strong { color: #17191d; }
.project { margin: 0 0 0.7mm; padding: 0 0 0.6mm 3.5mm; border-left: 0.6mm solid #d7b8bc; border-bottom: 0.25mm solid #e3e3e3; }
.project:last-child { border-bottom: none; padding-bottom: 0; }
.project h3 { margin: 0 0 0.2mm; font-size: 10.4pt; line-height: 1.18; color: #202226; }
.project p { margin: 0 0 0.3mm; font-size: 10pt; line-height: 1.28; color: #40444a; }
.tags { font-size: 8.3pt; line-height: 1.35; color: #8c1924; font-weight: 700; }
.small-list { margin: 0; padding-left: 4.5mm; font-size: 10pt; line-height: 1.35; }
.small-list li { margin-bottom: 1.2mm; }
.experience { margin: 0 0 0.7mm; padding-left: 3.5mm; border-left: 0.6mm solid #d7b8bc; }
.experience:last-child { margin-bottom: 0; }
.experience h3 { margin: 0 0 0.2mm; font-size: 10.2pt; line-height: 1.2; color: #202226; }
.experience .duration { float: right; color: #8c1924; font-size: 9.2pt; }
.experience p { margin: 0; font-size: 10pt; line-height: 1.25; color: #40444a; }
.note { font-size: 8.5pt; line-height: 1.25; color: #62666c; padding-top: 1.4mm; border-top: 0.3mm solid #d9d9d9; }
.footer { position: absolute; left: 16mm; right: 16mm; bottom: 7mm; display: flex; justify-content: space-between; color: #777b81; font-size: 8.2pt; }
.footer a { color: #777b81; text-decoration: none; }
</style>
</head>
<body>
<main class="page">
<header class="header">
<img class="photo" src="data:image/jpeg;base64,PHOTO_DATA" alt="Foto profesional M. Abdul Aziez">
<div>
<h1 class="name">M. Abdul Aziez</h1>
<p class="role">Web Developer | Mobile-First Business Systems</p>
<div class="contact">
<span>089514953909</span>
<a href="mailto:khususstokyunobi@gmail.com">khususstokyunobi@gmail.com</a>
<span>Indonesia</span>
<a href="https://visual-portfolio--portofoliosaya.replit.app/">Portfolio digital</a>
</div>
</div>
</header>

<div class="summary">
<p>Pengembang web berorientasi mobile yang menerjemahkan alur kerja bisnis menjadi sistem sederhana, cepat, dan siap dipakai. Berfokus pada arsitektur, logika bisnis, UI/UX, serta kendali mutu.</p>
</div>

<div class="content">
<section>
<h2>Pengalaman Kerja</h2>
<div class="experience">
<h3>Operator Mesin Produksi — Pabrik Sendal (Vendor) <span class="duration">1 tahun 2 bulan</span></h3>
<p>Mengoperasikan mesin produksi sendal.</p>
</div>
<div class="experience">
<h3>Sales Marketing — Toko Sembako Putra Jaya <span class="duration">5 bulan</span></h3>
<p>Penjualan dan pemasaran produk sembako.</p>
</div>
<div class="experience">
<h3>Kernet Sopir Barang <span class="duration">4 bulan</span></h3>
<p>Membantu sopir, angkat-jemput barang.</p>
</div>
</section>

<section>
<h2>Kompetensi inti</h2>
<p class="compact"><strong>Pengembangan:</strong> arsitektur aplikasi, logika bisnis, UI/UX mobile-first, Progressive Web App (PWA), sinkronisasi data langsung, dan kendali mutu.</p>
<p class="compact"><strong>Sistem operasional:</strong> kasir POS, manajemen pesanan, inventaris dan stok, pelacakan IMEI, absensi QR, akses multi-peran, dasbor keuangan, CRM, serta loyalty member.</p>
<p class="compact"><strong>Integrasi perangkat:</strong> printer termal USB/LAN/Bluetooth, layar sentuh, iOS, dan autentikasi biometrik.</p>
</section>

<section>
<h2>Fokus proyek dan solusi</h2>
<div class="project">
<h3>Klinik kecantikan &amp; operasional</h3>
<p>Sistem terpadu untuk kasir, jadwal layanan, absensi, stok produk, pesanan online, serta perhitungan komisi dokter dan terapis.</p>
<div class="tags">POS · JADWAL · ABSENSI QR · STOK · DASBOR OMZET</div>
</div>
<div class="project">
<h3>POS &amp; inventaris konter HP</h3>
<p>Alur transaksi yang memisahkan stok fisik dan saldo pulsa, dilengkapi pelacakan garansi per IMEI, piutang, serta pemantauan laba-rugi.</p>
<div class="tags">INVENTARIS · IMEI · PULSA · PIUTANG · NOTIFIKASI WA</div>
</div>
<div class="project">
<h3>Restoran &amp; kafe digital</h3>
<p>Alur pemesanan dari menu QR di meja menuju layar dapur, kasir, dan perhitungan biaya resep yang menyesuaikan stok bahan per porsi.</p>
<div class="tags">MENU QR · LAYAR DAPUR · POS · BIAYA RESEP</div>
</div>
<div class="project">
<h3>Multi-cabang &amp; loyalty CRM</h3>
<p>Monitoring terpusat untuk cabang, transfer stok, analitik operasional, poin member, dan kartu digital berbasis QR.</p>
<div class="tags">CABANG · TRANSFER STOK · CRM · MEMBER · KARTU QR</div>
</div>
</section>

<section>
<h2>Solusi tambahan</h2>
<p class="compact">Landing page UMKM dan profil bisnis · Pemesanan menu melalui WhatsApp · Dasbor keuangan UMKM · Reservasi jasa dan lapangan.</p>
</section>

<section>
<h2>Pendidikan</h2>
<p class="compact"><strong>SMKN 1 Mauk</strong> <span style="float:right">2020–2023</span></p>
<p class="compact"><strong>SMP Nurul Fallah Tanjakan Mekar</strong> <span style="float:right">2017–2020</span></p>
<p class="compact"><strong>SDN Tanjakan 2</strong> <span style="float:right">2011–2017</span></p>
<p class="compact">Ijazah hilang pasca pindahan rumah dan sedang dalam proses pengurusan ulang.</p>
</section>

<section>
<h2>Pendekatan kerja</h2>
<p class="compact">Memanfaatkan AI untuk mempercepat kode dasar dan penelusuran kesalahan, sambil mempertahankan kendali langsung atas arsitektur, logika bisnis, UI/UX, pengujian, dan kualitas hasil akhir.</p>
</section>

<section class="note">
<strong>Catatan administrasi:</strong> Kelengkapan berkas fisik lainnya, seperti SKCK dan NPWP, sedang dalam proses penataan atau pengurusan ulang setelah pindahan rumah dan siap dilampirkan menyusul.
</section>
</div>

<footer class="footer">
<span>CV berbasis portofolio profesional</span>
<span>M. Abdul Aziez</span>
</footer>
</main>
</body>
</html>'''.replace('PHOTO_DATA', photo)
(root / '.src/index.html').write_text(html, encoding='utf-8')
print(root / '.src/index.html')
