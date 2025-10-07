# Kurumsal Markdown'dan PDF'ye Dönüştürücü

Bu araç, `input` klasöründeki tüm Markdown (`.md`) dosyalarını modern ve sade bir kurumsal tasarımla PDF'e dönüştürür. Çıktılar `output` klasörüne kaydedilir.

## Kurulum

1. Python 3.8+ yüklü olmalı.
2. Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

> **Not:** Playwright ilk kurulumda ek indirme gerektirir:
>
> ```bash
> playwright install
> ```

## Kullanım

1. Dönüştürmek istediğiniz `.md` dosyalarını `input/` klasörüne ekleyin.
2. Terminalde proje klasörüne gelin ve çalıştırın:

```bash
python main.py
```

3. PDF çıktıları `output/` klasöründe oluşacaktır.

## Özellikler

- Sade ve modern kurumsal PDF tasarımı
- Markdown'dan otomatik PDF üretimi
- Listelerde tek tip işaret, başlıkta belge adı yok
- Kod blokları, tablolar ve alıntılar desteklenir

## Sorun Giderme

- Eğer PDF oluşmazsa, Playwright'ın kurulu ve Chromium'un indirilmiş olduğundan emin olun.
- Hata mesajlarını terminalde görebilirsiniz.

## Lisans

MIT
