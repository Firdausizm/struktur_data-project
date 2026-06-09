# Struktur Data Project

Proyek ini berisi implementasi struktur data sederhana dengan fokus pada penggunaan Trie pada mesin pencari buku. API di ambil dari google books, jadi pastikan utuk memiliki tokenya agar dapat menjalankan web ini.

## Cara Menjalankan Secara Lokal

1. Pastikan Python 3.11 atau lebih baru terpasang.
2. Buka terminal di folder proyek:
   ```powershell
   cd struktur_data-project
   ```
3. Aktifkan virtual environment :
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
4. Install dependency di`requirements.txt`:
   ```powershell
   pip install -r requirements.txt
   ```
5. Jalankan di enrty point ini:
   ```powershell
   python main.py
   ```


## Struktur Proyek

- `main.py` - titik masuk aplikasi.
- `src/` - implementasi struktur data Trie dan algoritma search engine.
- `frontend/` - halaman frontend sederhana.

## Cara Berkontribusi

1. Fork atau clone repositori ini.
2. Buat branch fitur atau perbaikan baru:
   ```powershell
   git checkout -b fitur/nama-fitur
   ```
3. Lakukan perubahan pada kode atau dokumentasi.
4. Pastikan perubahan masih berjalan dengan baik.
5. Commit dengan pesan jelas:
   ```powershell
   git add .
   git commit -m "Menambahkan fitur X atau memperbaiki bug Y"
   ```
6. Push branch ke remote:
   ```powershell
   git push origin fitur/nama-fitur
   ```
7. Buat pull request dan jelaskan perubahan yang dibuat.

## Catatan

- Selalu gunakan branch terpisah untuk setiap fitur atau perbaikan.
- Jika mengubah logika Trie atau alur utama, tambahkan komentar dan dokumentasi singkat di kode.
- Untuk kontribusi lebih besar, diskusikan terlebih dahulu sebelum membuat perubahan besar.
