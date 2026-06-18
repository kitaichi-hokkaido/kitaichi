# -*- coding: utf-8 -*-
import zipfile, shutil, re, os
from lxml import etree

src = "kitaichi_slides.pptx"
dst = "slides_small.pptx"

NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

zin = zipfile.ZipFile(src)
names = zin.namelist()

# keep only slideLayout1 (the master must keep >=1 layout). Our slides use blank layout
# but each slide rels point to a specific layout. Find which layouts slides reference.
slide_rels = [n for n in names if re.match(r"ppt/slides/_rels/slide\d+\.xml\.rels", n)]
used_layouts = set()
for sr in slide_rels:
    data = zin.read(sr).decode("utf-8")
    for m in re.finditer(r"slideLayouts/(slideLayout\d+)\.xml", data):
        used_layouts.add(m.group(1))
print("used layouts:", used_layouts)

keep_layouts = used_layouts  # only keep referenced ones
all_layouts = set(re.match(r".*/(slideLayout\d+)\.xml$", n).group(1)
                  for n in names if re.match(r"ppt/slideLayouts/slideLayout\d+\.xml$", n))
drop_layouts = all_layouts - keep_layouts
print("drop:", sorted(drop_layouts))

def is_dropped(name):
    for dl in drop_layouts:
        if name == f"ppt/slideLayouts/{dl}.xml" or name == f"ppt/slideLayouts/_rels/{dl}.xml.rels":
            return True
    return False

# Patch master xml + rels to remove references to dropped layouts
master_xml = zin.read("ppt/slideMasters/slideMaster1.xml")
master_rels = zin.read("ppt/slideMasters/_rels/slideMaster1.xml.rels")

# parse master rels: map rId -> layout target
rroot = etree.fromstring(master_rels)
drop_rids = set()
for rel in list(rroot):
    tgt = rel.get("Target")
    m = re.search(r"slideLayout(\d+)\.xml", tgt or "")
    if m and f"slideLayout{m.group(1)}" in drop_layouts:
        drop_rids.add(rel.get("Id"))
        rroot.remove(rel)
master_rels_new = etree.tostring(rroot, xml_declaration=True, encoding="UTF-8", standalone=True)

mroot = etree.fromstring(master_xml)
nsmap_p = mroot.nsmap.get("p")
for lst in mroot.iter("{http://schemas.openxmlformats.org/presentationml/2006/main}sldLayoutIdLst"):
    for child in list(lst):
        rid = child.get("{%s}id" % NS_R)
        if rid in drop_rids:
            lst.remove(child)
master_xml_new = etree.tostring(mroot, xml_declaration=True, encoding="UTF-8", standalone=True)

# Patch [Content_Types].xml to drop overrides for removed layouts
ct = zin.read("[Content_Types].xml")
croot = etree.fromstring(ct)
for ov in list(croot):
    pn = ov.get("PartName") or ""
    m = re.search(r"slideLayout(\d+)\.xml$", pn)
    if m and f"slideLayout{m.group(1)}" in drop_layouts:
        croot.remove(ov)
ct_new = etree.tostring(croot, xml_declaration=True, encoding="UTF-8", standalone=True)

zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for n in names:
    if is_dropped(n):
        continue
    if n == "ppt/slideMasters/slideMaster1.xml":
        zout.writestr(n, master_xml_new)
    elif n == "ppt/slideMasters/_rels/slideMaster1.xml.rels":
        zout.writestr(n, master_rels_new)
    elif n == "[Content_Types].xml":
        zout.writestr(n, ct_new)
    else:
        zout.writestr(n, zin.read(n))
zout.close()
print("size", os.path.getsize(dst))
