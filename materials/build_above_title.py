import sys, pathlib
from weasyprint import HTML
import pypdfium2 as pdfium

base = pathlib.Path('kitaichi_overview_a4.html').read_text(encoding='utf-8')

p1 = sys.argv[1] if len(sys.argv) > 1 else None  # left: students
p2 = sys.argv[2] if len(sys.argv) > 2 else None  # right: Kaminokuni CF
PH = sys.argv[3] if len(sys.argv) > 3 else '46'   # photo band height (mm)


def cell(path, pos, cls):
    if path:
        inner = f'<img src="{path}" style="object-position:{pos};" alt="">'
    else:
        inner = '<div class="ph">［ 写真がここに入ります ］</div>'
    return f'<div class="tp-cell {cls}">{inner}</div>'


top_css = '''
  .topphotos { display:flex; gap:7pt; margin:0 0 6pt; align-items:flex-start; }
  .topphotos .tp-cell.left  { width:38%; }
  .topphotos .tp-cell.right { width:62%; }
  .topphotos img, .topphotos .ph {
    width:100%; height:HEIGHTmm; object-fit:cover; display:block;
    border-radius:3pt; }
  .topphotos .tp-cell.contain img { object-fit:contain; object-position:center; }
  .topphotos .ph { background:#e3ecec; color:#8a9a9a; font-size:8.5pt;
    display:flex; align-items:center; justify-content:center; }
'''

band = ('  <div class="topphotos">\n    '
        + cell(p1, 'center', 'left contain') + '\n    '
        + cell(p2, 'center', 'right') + '\n  </div>\n\n')

top_css = top_css.replace('HEIGHT', PH)
html = base.replace('</style>', top_css + '</style>')
# insert the photo band ABOVE the doctitle banner
html = html.replace(
    '  <div class="doctitle">',
    band + '  <div class="doctitle">'
)

pathlib.Path('variant_AB.html').write_text(html, encoding='utf-8')
HTML('variant_AB.html').write_pdf('variant_AB.pdf')
d = pdfium.PdfDocument('variant_AB.pdf')
print('pages:', len(d))
d[0].render(scale=2.2).to_pil().save('preview_AB.png')
print('done')
