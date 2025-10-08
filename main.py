# corporate_pdf_with_images.py
#!/usr/bin/env python3
import markdown
import yaml
from pathlib import Path
from playwright.sync_api import sync_playwright
from jinja2 import Template
import base64
import os

class CorporatePDFConverter:
    def __init__(self):
        self.input_dir = Path("input")
        self.output_dir = Path("output")
        self.images_dir = Path("images")
        self.output_dir.mkdir(exist_ok=True)
    
    def get_template(self):
        """Modern kurumsal template with image support"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset='UTF-8'>
            <title></title>
            <style>
                :root {
                    --primary: #1a365d;
                    --accent: #3182ce;
                    --text: #222;
                    --border: #e2e8f0;
                    --code-bg: #f5f7fa;
                }
                body {
                    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                    font-size: 11pt;
                    color: var(--text);
                    background: #fff;
                    margin: 0;
                    padding: 2cm 2cm;
                }
                .content {
                    margin: 0 auto;
                    max-width: 800px;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: var(--primary);
                    font-weight: 600;
                    margin-top: 1.2em;
                    margin-bottom: 0.5em;
                }
                h1 { font-size: 20pt; border-bottom: 1px solid var(--border); padding-bottom: 0.2em; }
                h2 { font-size: 16pt; border-bottom: 1px solid #f0f0f0; }
                h3 { font-size: 13pt; }
                h4 { font-size: 11.5pt; }
                p {
                    margin-bottom: 0.8em;
                    text-align: left;
                }
                code, pre {
                    background: var(--code-bg);
                    border-radius: 5px;
                    font-family: 'JetBrains Mono', 'Consolas', monospace;
                    font-size: 10pt;
                }
                code {
                    padding: 0.1em 0.4em;
                    color: #1a365d;
                }
                pre {
                    padding: 1em;
                    margin: 1em 0;
                    overflow-x: auto;
                }
                pre code {
                    background: none;
                    padding: 0;
                }
                blockquote {
                    border-left: 4px solid var(--accent);
                    margin: 1em 0;
                    padding: 0.5em 1em;
                    color: #555;
                    background: #f7fafc;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 1em 0;
                    font-size: 10pt;
                }
                th, td {
                    border: 1px solid var(--border);
                    padding: 0.5em 0.8em;
                }
                th {
                    background: #f0f4fa;
                    color: var(--primary);
                }
                ul, ol {
                    margin-bottom: 0.8em;
                    padding-left: 1.2em;
                }
                li {
                    margin-bottom: 0.3em;
                    position: relative;
                }
                /* Image styles */
                img {
                    max-width: 100%;
                    height: auto;
                    display: block;
                    margin: 1em auto;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    border: 1px solid #e2e8f0;
                }
                /* Mobil görüntüler için küçük boyut */
                img[width="250"] {
                    max-width: 250px;
                }
                /* Web görüntüler için büyük boyut */
                img[width="600"] {
                    max-width: 600px;
                }
                /* Sadece tek tip işaret: ul ve ol için varsayılanı kullan, ::marker ile özelleştir */
                ul li::marker {
                    content: "• ";
                    color: var(--accent);
                    font-size: 1.1em;
                }
                ol li::marker {
                    color: var(--accent);
                    font-weight: bold;
                }
                a {
                    color: var(--accent);
                    text-decoration: none;
                    border-bottom: 1px solid #cce4ff;
                }
                @media print {
                    body { padding: 1.2cm 1.2cm; }
                    img {
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                }
            </style>
        </head>
        <body>
            <div class="content">
                {{content}}
            </div>
        </body>
        </html>
        """
    
    def image_to_base64(self, image_path):
        """Image'i base64 formatına çevir"""
        try:
            if image_path.exists():
                with open(image_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                extension = image_path.suffix.lower()
                if extension == '.png':
                    return f"data:image/png;base64,{encoded_string}"
                elif extension in ['.jpg', '.jpeg']:
                    return f"data:image/jpeg;base64,{encoded_string}"
                elif extension == '.gif':
                    return f"data:image/gif;base64,{encoded_string}"
                else:
                    return f"data:image/png;base64,{encoded_string}"
            else:
                print(f"⚠️  Image bulunamadı: {image_path}")
                return None
        except Exception as e:
            print(f"❌ Image conversion hatası: {e}")
            return None
    
    def replace_image_paths(self, html_content, md_file_path):
        """HTML içindeki image path'lerini base64 formatına çevir"""
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Tüm img tag'lerini bul
        for img in soup.find_all('img'):
            src = img.get('src', '')
            
            # Relative path kontrolü (../images/ şeklinde)
            if src.startswith('../images/'):
                image_filename = src.replace('../images/', '')
                image_path = self.images_dir / image_filename
                
                # Base64'e çevir
                base64_data = self.image_to_base64(image_path)
                if base64_data:
                    img['src'] = base64_data
                    print(f"✅ Image eklendi: {image_filename}")
                else:
                    # Image bulunamazsa placeholder ekle
                    img['src'] = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjVmN2ZhIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk0YTBhYiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4="
                    print(f"❌ Image bulunamadı: {image_filename}")
            
            # Diğer relative path formatları
            elif src.startswith('./images/') or src.startswith('images/'):
                image_filename = src.split('/')[-1]
                image_path = self.images_dir / image_filename
                
                base64_data = self.image_to_base64(image_path)
                if base64_data:
                    img['src'] = base64_data
                    print(f"✅ Image eklendi: {image_filename}")
        
        return str(soup)
    
    def convert_file(self, md_file):
        """Tek bir dosyayı dönüştür"""
        try:
            print(f"📖 İşleniyor: {md_file.name}")
            
            # Dosyayı oku
            content = md_file.read_text(encoding='utf-8')
            
            # Front matter ayır
            lines = content.split('\n')
            front_matter = {}
            if lines and lines[0].strip() == '---':
                yaml_lines = []
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        content = '\n'.join(lines[i+1:])
                        break
                    yaml_lines.append(line)
                try:
                    front_matter = yaml.safe_load('\n'.join(yaml_lines)) or {}
                except:
                    front_matter = {}
            
            # Markdown -> HTML
            html_content = markdown.markdown(
                content, 
                extensions=['extra', 'fenced_code', 'tables', 'codehilite'],
                extension_configs={
                    'codehilite': {
                        'css_class': 'highlight',
                        'guess_lang': False,
                        'linenums': False
                    }
                }
            )
            
            # Image path'lerini base64 formatına çevir
            html_content = self.replace_image_paths(html_content, md_file)
            
            # Metadata
            title = front_matter.get('title', md_file.stem)
            author = front_matter.get('author', '')
            
            # Template doldur
            template = Template(self.get_template())
            final_html = template.render(
                title="",
                author="",
                content=html_content,
                show_header=False,
                show_footer=False
            )
            
            # PDF oluştur
            pdf_path = self.output_dir / f"{md_file.stem}.pdf"
            
            with sync_playwright() as p:
                # Headless modda browser başlat
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # A4 portrait için viewport ayarla
                page.set_viewport_size({"width": 1240, "height": 1754})
                
                # HTML içeriğini yükle
                page.set_content(final_html, wait_until='networkidle')
                
                # A4 Portrait PDF oluştur
                page.pdf(
                    path=str(pdf_path),
                    format='A4',
                    landscape=False,
                    margin={'top': '1.5cm', 'right': '1.5cm', 'bottom': '1.5cm', 'left': '1.5cm'},
                    display_header_footer=False,
                    print_background=True
                )
                
                browser.close()
            
            print(f"✅ Başarılı: {pdf_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_images(self):
        """Image'leri kontrol et"""
        print("🔍 Image'ler kontrol ediliyor...")
        image_files = list(self.images_dir.rglob("*.*"))
        if not image_files:
            print("❌ images/ klasöründe image bulunamadı!")
            return False
        print(f"📸 {len(image_files)} image bulundu:")
        for img in image_files:
            print(f"   - {img.relative_to(self.images_dir)}")
        return True
    
    def convert_all(self):
        """Tüm dosyaları dönüştür"""
        # Önce image'leri kontrol et
        if not self.check_images():
            return
        
        md_files = list(self.input_dir.glob("*.md"))
        
        if not md_files:
            print("❌ input klasöründe .md dosyası bulunamadı!")
            return
        
        print(f"📁 {len(md_files)} dosya bulundu...")
        
        success = 0
        for md_file in md_files:
            print(f"\n🔨 İşleniyor: {md_file.stem}")
            if self.convert_file(md_file):
                success += 1
            else:
                print(f"❌ Başarısız: {md_file.stem}")
        
        print(f"\n🎉 İşlem tamamlandı: {success}/{len(md_files)} dosya başarıyla dönüştürüldü!")
        print(f"📂 Çıktılar: {self.output_dir}/")

def main():
    """Ana fonksiyon"""
    print("🚀 Kurumsal MD to PDF Converter (Image Desteğiyle)")
    print("=" * 50)
    
    converter = CorporatePDFConverter()
    converter.convert_all()

if __name__ == "__main__":
    # Gerekli kütüphaneleri kontrol et
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("❌ BeautifulSoup4 kurulu değil. Lütfen kurun:")
        print("pip install beautifulsoup4")
        exit(1)
    
    main()