import sys, pathlib
from weasyprint import HTML
import pypdfium2 as pdfium

base = pathlib.Path('kitaichi_overview_a4.html').read_text(encoding='utf-8')

# optional image paths: photo1 photo2
p1 = sys.argv[1] if len(sys.argv) > 1 else None
p2 = sys.argv[2] if len(sys.argv) > 2 else None


def cell(path, caption, pos='center', cls=''):
    if path:
        style = f' style="object-position:{pos};"' if pos else ''
        inner = f'<img src="{path}"{style} alt="">'
    else:
        inner = '<div class="ph">［ 写真がここに入ります ］</div>'
    return f'<div class="tp-cell {cls}">{inner}<div class="pcap">{caption}</div></div>'


top_css = '''
  .topphotos { display:flex; gap:7pt; margin:0 0 7pt; align-items:flex-start; }
  .topphotos .tp-cell.left  { width:46%; }
  .topphotos .tp-cell.right { width:54%; }
  .topphotos img, .topphotos .ph {
    width:100%; height:29mm; object-fit:cover; display:block;
    border-radius:3pt; }
  .topphotos .ph { background:#e3ecec; color:#8a9a9a; font-size:8.5pt;
    display:flex; align-items:center; justify-content:center; }
  .topphotos .pcap { font-size:7pt; color:#5a6b6b; padding:2pt 1pt 0; text-align:center; }
'''

band = ('  <div class="topphotos">\n    '
        + cell(p1, 'KITAICHIチーム ─ 夕張の拠点にて', pos='center 30%', cls='left') + '\n    '
        + cell(p2, '代表　佐近　航（さこん わたる）', pos='center 22%', cls='right') + '\n  </div>\n\n')

html = base.replace('</style>', top_css + '</style>')
# insert the photo band right after the doctitle, before the first .cols
html = html.replace(
    '  <!-- 上段：会社概要 ＋ 代表メッセージ -->\n  <div class="cols">',
    band + '  <!-- 上段：会社概要 ＋ 代表メッセージ -->\n  <div class="cols">'
)

pathlib.Path('variant_T.html').write_text(html, encoding='utf-8')
HTML('variant_T.html').write_pdf('variant_T.pdf')
d = pdfium.PdfDocument('variant_T.pdf')
print('pages:', len(d))
d[0].render(scale=2.2).to_pil().save('preview_T.png')
print('done')
