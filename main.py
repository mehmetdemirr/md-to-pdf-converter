# corporate_pdf_final.py
#!/usr/bin/env python3
import markdown
import yaml
from pathlib import Path
from playwright.sync_api import sync_playwright
from jinja2 import Template

class CorporatePDFConverter:
    def __init__(self):
        self.input_dir = Path("input")
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def get_template(self):
        """Modern kurumsal template"""
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
    
    def convert_file(self, md_file):
        """Tek bir dosyayı dönüştür"""
        try:
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
            
            # Metadata
            title = front_matter.get('title', md_file.stem)
            author = front_matter.get('author', '')
            
            # Template doldur
            template = Template(self.get_template())
            # PDF başında belge adı/başlık gösterilmesin, header tamamen kaldırıldı
            final_html = template.render(
                title="",  # başlık boş
                author="", # yazar boş
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
            
            return True
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            return False
    
    def convert_all(self):
        """Tüm dosyaları dönüştür"""
        md_files = list(self.input_dir.glob("*.md"))
        
        if not md_files:
            print("❌ input klasöründe .md dosyası bulunamadı!")
            return
        
        print(f"📁 {len(md_files)} dosya bulundu...")
        
        success = 0
        for md_file in md_files:
            print(f"🔨 İşleniyor: {md_file.stem}")
            if self.convert_file(md_file):
                success += 1
                print(f"✅ Başarılı: {md_file.stem}.pdf")
            else:
                print(f"❌ Başarısız: {md_file.stem}")
        
        print(f"\n🎉 İşlem tamamlandı: {success}/{len(md_files)} dosya başarıyla dönüştürüldü!")
        print(f"📂 Çıktılar: {self.output_dir}/")

def main():
    """Ana fonksiyon"""
    print("🚀 Kurumsal MD to PDF Converter")
    print("=" * 40)
    
    converter = CorporatePDFConverter()
    converter.convert_all()

if __name__ == "__main__":
    main()