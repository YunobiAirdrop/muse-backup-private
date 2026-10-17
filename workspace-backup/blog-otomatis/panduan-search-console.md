# Panduan Google Search Console (sekali setup, ~10 menit per blog)

Search Console bikin artikel ke-index Google dalam hitungan jam, bukan hari.
Ini HARUS kamu yang lakukan (butuh login akun Google pemilik blog).

## Langkah per blog (ulangi 4x)

1. Buka https://search.google.com/search-console
2. Klik **Tambahkan properti** → pilih **Awalan URL** → masukkan URL blog, misal:
   `https://kabarviralterkiniterbaru.blogspot.com/` → Lanjutkan
3. Verifikasi kepemilikan: pilih metode **Tag HTML**, copy tag-nya,
   tempel di Blogger → Tema → Edit HTML → tepat setelah `<head>` → Simpan.
   Kembali ke Search Console → klik **Verifikasi**.
   (4 blog = 4 akun Google berbeda — pastikan login akun yang benar per blog!)
4. Di menu kiri → **Peta situs** → masukkan `sitemap.xml` → Kirim.
   Sitemap 4 blog (sudah dicek hidup semua):
   - https://kabarviralterkiniterbaru.blogspot.com/sitemap.xml
   - https://cuanpintarterbaruviral.blogspot.com/sitemap.xml
   - https://teknogebrakan.blogspot.com/sitemap.xml
   - https://sehatbugarterbaru.blogspot.com/sitemap.xml
5. Selesai. 2-3 hari kemudian cek menu **Halaman** → pastikan artikel mulai ter-index.

## Tips
- Artikel yang belum ke-index setelah 3 hari: copy URL-nya → menu **Inspeksi URL** → **Minta pengindeksan**.
- Jangan submit URL manual tiap hari untuk semua artikel (dianggap spam) — cukup yang penting saja.
