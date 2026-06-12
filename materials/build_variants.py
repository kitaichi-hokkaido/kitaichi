import sys, re, pathlib
from weasyprint import HTML

base = pathlib.Path('kitaichi_overview_a4.html').read_text(encoding='utf-8')

# image source: placeholder or real file passed as arg
img = sys.argv[1] if len(sys.argv) > 1 else None

def photo_block(kind):
    # case C uses a vertically-tightened banner crop so heads & feet stay in frame
    src_file = ('team_banner.jpg' if (img and kind == 'C') else img)
    if img:
        src = f'<img src="{src_file}" alt="KITAICHIチーム">'
    else:
        src = '<div class="ph">チーム写真が入ります（プレースホルダー）</div>'
    cap = '<div class="pcap">KITAICHIチーム ─ 夕張の拠点にて</div>'
    cls = 'photo-a' if kind == 'A' else 'photo-c'
    return f'<div class="photo {cls}">{src}{cap}</div>'

# common photo CSS injected before </style>
photo_css = '''
  .photo { border-radius:3pt; }
  .photo .ph { background:#e3ecec; color:#7a8a8a; text-align:center; font-size:8pt;
               display:flex; align-items:center; justify-content:center; }
  .photo .pcap { font-size:7pt; color:#5a6b6b; padding:2pt 1pt 0; text-align:center; }
  /* A: full-width cover banner at top of right column */
  .photo-a { margin-bottom:5pt; overflow:hidden; border-radius:3pt; }
  .photo-a img, .photo-a .ph { width:100%; display:block; object-fit:cover; height:30mm; }
  /* C: centered horizontal photo, whole team visible (no heavy crop) */
  .photo-c { margin:6pt 0 5pt; text-align:center; }
  .photo-c img { height:43mm; width:auto; max-width:100%; display:inline-block;
                 border-radius:3pt; box-shadow:0 0 0 0.6pt #d3dede; }
'''

# ---- Variant A: photo at top of right column (above 代表メッセージ) ----
htmlA = base.replace('</style>', photo_css + '</style>')
# insert before the right column h2 代表メッセージ
htmlA = htmlA.replace(
    '<div class="col-right">\n      <h2>代表メッセージ</h2>',
    '<div class="col-right">\n      ' + photo_block('A') + '\n      <h2>代表メッセージ</h2>'
)
# shorten message a touch so A still fits one page
htmlA = htmlA.replace(
    '誰もが新しい一歩を踏み出せずにいたなか、夕張高校の生徒会長が「夕張に言い訳するのではなく、夕張だからできることに目を向けたい」と大人たちへ語りかけ、その言葉が抜本的な再生計画の見直しを動かしました。',
    '夕張高校の生徒会長が「夕張に言い訳するのではなく、夕張だからできることに目を向けたい」と大人たちへ語りかけ、その言葉が抜本的な再生計画の見直しを動かしました。'
)

# ---- Variant C: photo as wide banner near bottom (above contact) ----
htmlC = base.replace('</style>', photo_css + '</style>')
htmlC = htmlC.replace(
    '  <div class="contact">',
    '  ' + photo_block('C') + '\n\n  <div class="contact">'
)

pathlib.Path('variant_A.html').write_text(htmlA, encoding='utf-8')
pathlib.Path('variant_C.html').write_text(htmlC, encoding='utf-8')

for name in ['A', 'C']:
    out = f'preview_{name}.png'
    pdf = f'variant_{name}.pdf'
    doc = HTML(f'variant_{name}.html')
    doc.write_pdf(pdf)
    import pypdfium2 as pdfium
    d = pdfium.PdfDocument(pdf)
    print(name, 'pages:', len(d))
    d[0].render(scale=2.0).to_pil().save(out)
print('done')
