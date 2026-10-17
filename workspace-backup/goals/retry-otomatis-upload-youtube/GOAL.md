# Retry otomatis upload YouTube

Goal ID: goal_62a68750035a
Goal slug: retry-otomatis-upload-youtube

## Description
Sistem retry otomatis agar tidak ada video YouTube yang mogok diam-diam. Jika upload gagal karena batas harian, video masuk antrean JSON; watchdog harian mengerjakan ulang antrean yang umurnya minimal 23 jam dengan ketukan persetujuan Yunobi, dan kegagalan non-limit langsung dicoba ulang saat itu juga.
