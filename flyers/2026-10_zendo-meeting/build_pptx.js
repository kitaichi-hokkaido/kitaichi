// チラシたたき台（A4両面）を編集可能な .pptx として書き出す
// 使い方: node build_pptx.js  （pptxgenjs が必要: npm install pptxgenjs）
const pptxgen = require("pptxgenjs");

const W = 8.27, H = 11.69, M = 0.47; // A4縦（インチ）・左右余白
const CW = W - M * 2;
const C = {
  navy: "16324F", blue: "2A6F97", sky: "E6F1F7", accent: "F28C28", accentSoft: "FFF1E3",
  ink: "1F2933", muted: "5B6770", line: "D5DDE3", ph: "DFE6EB", phLine: "9AA8B3",
  todo: "D7263D", gold: "FFD08A", white: "FFFFFF",
};
const FONT = "Noto Sans JP";

const pres = new pptxgen();
pres.defineLayout({ name: "A4P", width: W, height: H });
pres.layout = "A4P";
pres.title = "全道meeting配布チラシ（クラファン伴走サポート）";

// 【…】で囲まれた箇所を赤字にしたテキストランを作る
function runs(str, base = {}) {
  return str.split(/(【[^】]*】)/).filter(Boolean).map((s) => ({
    text: s,
    options: s.startsWith("【") ? { ...base, color: C.todo, bold: true } : { ...base },
  }));
}
function text(slide, content, opts) {
  slide.addText(typeof content === "string" ? runs(content) : content, {
    fontFace: FONT, color: C.ink, fontSize: 10, margin: 0, valign: "top", isTextBox: true, ...opts,
  });
}
function placeholder(slide, label, x, y, w, h, extra = {}) {
  slide.addText(label, {
    shape: pres.shapes.RECTANGLE, x, y, w, h, fontFace: FONT, fontSize: 9, color: C.muted,
    align: "center", valign: "middle", fill: { color: C.ph },
    line: { color: C.phLine, width: 1, dashType: "dash" }, isTextBox: true, ...extra,
  });
}
function heading(slide, label, x, y, w, color = C.navy, mark = C.accent) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: y + 0.05, w: 0.07, h: 0.22, fill: { color: mark }, rectRadius: 0.02 });
  text(slide, label, { x: x + 0.15, y, w: w - 0.15, h: 0.32, fontSize: 15, bold: true, color, valign: "middle" });
}
function pill(slide, label, x, y, w, fill, color, fontSize = 8.5) {
  slide.addText(label, {
    shape: pres.shapes.ROUNDED_RECTANGLE, x, y, w, h: 0.24, rectRadius: 0.12, fill: { color: fill },
    fontFace: FONT, fontSize, bold: true, color, align: "center", valign: "middle", margin: 0, isTextBox: true,
  });
}

// ======================= 表面 =======================
const f = pres.addSlide();
f.background = { color: C.white };

// タイトル
f.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 2.8, fill: { color: C.navy }, line: { color: C.navy } });
f.addText("地域おこし協力隊のみなさまへ", {
  shape: pres.shapes.ROUNDED_RECTANGLE, x: M, y: 0.42, w: 2.45, h: 0.32, rectRadius: 0.04,
  fill: { color: C.accent }, fontFace: FONT, fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle", margin: 0, isTextBox: true,
});
text(f, [
  { text: "その「やりたい」、", options: { breakLine: true } },
  { text: "クラウドファンディング", options: { color: C.gold } },
  { text: "で", options: { breakLine: true } },
  { text: "全国の応援に変えませんか？" },
], { x: M, y: 0.88, w: CW, h: 1.45, fontSize: 26, bold: true, color: C.white, lineSpacingMultiple: 1.05 });
text(f, "企画づくりから公開後まで、KITAICHIがクラファンを伴走サポートします。",
  { x: M, y: 2.35, w: CW, h: 0.26, fontSize: 11.5, color: C.white });

// 写真
placeholder(f, "【要差替】写真：協力隊の活動風景／支援プロジェクトの現場\n（写真を挿入して、この枠は削除してください）", 0, 2.8, W, 2.1, { line: { color: C.phLine, width: 0 } });

// 悩み → サービス
heading(f, "クラファン、気になっているけど…", M, 5.08, CW);
const worries = ["何から始めればいいか分からない", "本業の活動が忙しくて手が回らない", "リターンや目標金額の決め方が不安", "集まらなかったらどうしよう"];
const gap = 0.1, cw4 = (CW - gap * 3) / 4;
worries.forEach((w, i) => {
  f.addText([{ text: "？ ", options: { color: C.blue, bold: true } }, { text: w }], {
    shape: pres.shapes.ROUNDED_RECTANGLE, x: M + i * (cw4 + gap), y: 5.48, w: cw4, h: 0.5, rectRadius: 0.06,
    fill: { color: C.sky }, fontFace: FONT, fontSize: 9, color: C.ink, valign: "middle", margin: [2, 6, 2, 6], isTextBox: true,
  });
});
text(f, "▼ KITAICHIが、ぜんぶ一緒に考えます ▼", { x: M, y: 6.04, w: CW, h: 0.28, fontSize: 11, bold: true, color: C.accent, align: "center", valign: "middle" });

const services = [
  ["STEP 1", "企画・設計", "活動の想いを整理し、目標金額・リターン・スケジュールを一緒に設計。"],
  ["STEP 2", "ページ制作", "伝わる文章・写真・構成で、応援したくなるプロジェクトページに。"],
  ["STEP 3", "広報・集客", "SNS・プレスリリース・地域メディアへの発信で支援者を広げます。"],
  ["STEP 4", "終了後フォロー", "リターン発送や支援者との関係づくりまでサポート。"],
];
services.forEach(([step, title, body], i) => {
  const x = M + i * (cw4 + gap), y = 6.38;
  f.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw4, h: 1.2, rectRadius: 0.06, fill: { color: C.white }, line: { color: C.line, width: 1 } });
  f.addText(String(i + 1), {
    shape: pres.shapes.OVAL, x: x + 0.1, y: y + 0.1, w: 0.28, h: 0.28, fill: { color: C.blue },
    fontFace: FONT, fontSize: 10, bold: true, color: C.white, align: "center", valign: "middle", margin: 0, isTextBox: true,
  });
  text(f, step, { x: x + 0.44, y: y + 0.1, w: cw4 - 0.5, h: 0.28, fontSize: 8, bold: true, color: C.blue, valign: "middle", charSpacing: 1 });
  text(f, title, { x: x + 0.1, y: y + 0.42, w: cw4 - 0.2, h: 0.26, fontSize: 11.5, bold: true, color: C.navy });
  text(f, body, { x: x + 0.1, y: y + 0.7, w: cw4 - 0.2, h: 0.46, fontSize: 8, lineSpacingMultiple: 1.1 });
});
text(f, "【要確認】サービス内容・料金体系（例：成功報酬型／初期費用0円 等）を記載するか", { x: M, y: 7.63, w: CW, h: 0.22, fontSize: 8.5 });

// KITAICHIについて
heading(f, "KITAICHIについて", M, 7.95, CW);
placeholder(f, "【要差替】\nロゴ", M, 8.35, 1.3, 0.8);
text(f, runs("北海道を拠点に、地域の挑戦をクラウドファンディングで後押ししている会社です。【要差替】設立年・所在地・ミッション・代表者の一言など", { fontSize: 9.5 }),
  { x: M + 1.45, y: 8.33, w: CW - 1.45, h: 0.48, lineSpacingMultiple: 1.1 });
[["支援実績 ○○件", 1.3], ["累計支援額 ○○万円", 1.55], ["達成率 ○○％", 1.15]].reduce((x, [l, w]) => {
  pill(f, l, x, 8.88, w, C.sky, C.navy);
  return x + w + 0.1;
}, M + 1.45);
text(f, "←【要差替】", { x: M + 1.45 + 4.3, y: 8.88, w: 1.0, h: 0.24, fontSize: 8.5, valign: "middle" });

// お問い合わせ（CTA）
const cy = 9.35;
f.addShape(pres.shapes.RECTANGLE, { x: 0, y: cy, w: W, h: H - cy, fill: { color: C.accentSoft }, line: { color: C.accentSoft } });
f.addText("全道meeting参加者限定・先着5名", {
  shape: pres.shapes.ROUNDED_RECTANGLE, x: M, y: cy + 0.2, w: 2.55, h: 0.3, rectRadius: 0.04,
  fill: { color: C.accent }, fontFace: FONT, fontSize: 10.5, bold: true, color: C.white, align: "center", valign: "middle", margin: 0, isTextBox: true,
});
text(f, "無料オンライン相談、受付中！", { x: M, y: cy + 0.55, w: 5.5, h: 0.42, fontSize: 19, bold: true, color: C.navy, valign: "middle" });
text(f, ["アイデア段階・まだ何も決まっていなくてもOK", "30分・オンライン（Zoom等）で気軽に", "相談したからといって、依頼の義務はありません"].flatMap((t, i, a) => [
  { text: "✓ ", options: { color: C.accent, bold: true } },
  { text: t, options: i < a.length - 1 ? { breakLine: true } : {} },
]), { x: M, y: cy + 1.0, w: 5.5, h: 0.6, fontSize: 9.5, lineSpacingMultiple: 1.15 });
f.addShape(pres.shapes.LINE, { x: M, y: cy + 1.66, w: 5.6, h: 0, line: { color: "E4B98B", width: 0.75, dashType: "dash" } });
text(f, [
  { text: "株式会社KITAICHI", options: { bold: true, color: C.navy } },
  ...runs("　【要確認】正式社名", {}), { text: "", options: { breakLine: true } },
  ...runs("MAIL：【要差替】　TEL：【要差替】　WEB：【要差替】"), { text: "", options: { breakLine: true } },
  ...runs("受付期限：【要差替】2026年○月○日（○）まで"),
], { x: M, y: cy + 1.72, w: 5.6, h: 0.55, fontSize: 9, lineSpacingMultiple: 1.1 });
placeholder(f, "【要差替】\n予約フォーム\nQR", W - M - 1.25, cy + 0.45, 1.25, 1.25, { fill: { color: C.white } });
text(f, "QRから30秒で予約", { x: W - M - 1.55, y: cy + 1.75, w: 1.55, h: 0.22, fontSize: 8.5, bold: true, color: C.navy, align: "center" });

// ======================= 裏面 =======================
const b = pres.addSlide();
b.background = { color: C.white };
b.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 1.9, fill: { color: C.navy }, line: { color: C.navy } });
text(b, "CASE STUDY ／ クラファン事例", { x: M, y: 0.35, w: CW, h: 0.25, fontSize: 10, bold: true, color: C.gold, charSpacing: 1 });
text(b, "協力隊の活動も、クラファンで\nこんなふうに広がりました。", { x: M, y: 0.62, w: CW, h: 0.82, fontSize: 21, bold: true, color: C.white, lineSpacingMultiple: 1.05 });
text(b, "あなたの地域・あなたの活動でも、きっとできます。", { x: M, y: 1.47, w: CW, h: 0.25, fontSize: 10.5, color: C.white });

const cases = [
  { no: "CASE 01", area: "○○町", theme: "特産品開発", title: "【要差替】規格外の○○を使った新商品を、町の新しい名物に",
    issue: "商品開発の初期費用と、町外への認知不足。", act: "完成品をリターンにして、先行予約型のクラファンを実施。",
    voice: "「【要差替】協力隊・事業者の声。支援者とのつながりが販路拡大に、など」" },
  { no: "CASE 02", area: "○○市", theme: "拠点づくり", title: "【要差替】空き家を改修して、移住者と地域が集まる拠点に",
    issue: "改修費が補助金だけでは足りない。", act: "改修ワークショップ参加権や命名権をリターンに設定。",
    voice: "「【要差替】協力隊の声。任期後の起業・定住につながった、など」" },
  { no: "CASE 03", area: "○○村", theme: "イベント・観光", title: "【要差替】途絶えかけた地域のお祭りを、全国の応援で復活",
    issue: "担い手不足と運営費の確保。", act: "関係人口づくりを狙い、当日参加・オンライン参加型のリターンを用意。",
    voice: "「【要差替】協力隊・地域の方の声。ファンが翌年も来てくれた、など」" },
];
const caseH = 2.45, caseGap = 0.18, startY = 2.12;
cases.forEach((c, i) => {
  const y = startY + i * (caseH + caseGap);
  b.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: CW, h: caseH, rectRadius: 0.08, fill: { color: C.white }, line: { color: C.line, width: 1 } });
  placeholder(b, `【要差替】\n事例${i + 1}の写真`, M + 0.15, y + 0.15, 1.95, caseH - 0.3);
  const x = M + 2.3, w = CW - 2.3 - 0.18;
  pill(b, c.no, x, y + 0.17, 0.8, C.navy, C.white, 8.5);
  pill(b, c.area, x + 0.88, y + 0.17, 0.7, C.sky, C.blue, 8.5);
  pill(b, c.theme, x + 1.66, y + 0.17, 1.05, C.sky, C.blue, 8.5);
  text(b, runs(c.title, { color: C.navy }), { x, y: y + 0.5, w, h: 0.3, fontSize: 12, bold: true, valign: "middle" });
  [["課題", c.issue], ["挑戦", c.act]].forEach(([k, v], j) => {
    text(b, k, { x, y: y + 0.88 + j * 0.25, w: 0.45, h: 0.22, fontSize: 9, bold: true, color: C.blue });
    text(b, v, { x: x + 0.5, y: y + 0.88 + j * 0.25, w: w - 0.5, h: 0.22, fontSize: 9 });
  });
  const rw = (w - 0.2) / 3;
  [["支援総額", "○○○万円"], ["支援者数", "○○○人"], ["達成率", "○○○％"]].forEach(([k, v], j) => {
    b.addText([
      { text: k, options: { fontSize: 7.5, bold: true, color: C.muted, breakLine: true } },
      { text: v, options: { fontSize: 14, bold: true, color: C.accent } },
    ], {
      shape: pres.shapes.ROUNDED_RECTANGLE, x: x + j * (rw + 0.1), y: y + 1.42, w: rw, h: 0.55, rectRadius: 0.05,
      fill: { color: C.accentSoft }, fontFace: FONT, align: "center", valign: "middle", margin: 0, isTextBox: true,
    });
  });
  text(b, runs(c.voice), { x, y: y + 2.05, w, h: 0.26, fontSize: 8.5, color: C.muted, valign: "middle" });
});

// 裏面CTA
const by = startY + 3 * caseH + 2 * caseGap + 0.25;
b.addShape(pres.shapes.RECTANGLE, { x: 0, y: by, w: W, h: H - by, fill: { color: C.navy }, line: { color: C.navy } });
heading(b, "次は、あなたの番です。", M, by + 0.42, 5.8, C.white, C.gold);
text(b, runs("「自分の活動でもできる？」まずは無料相談でお気軽にどうぞ。\n全道meeting参加者限定・先着5名／MAIL：○○○@○○○（要差替）", { color: C.white }),
  { x: M, y: by + 0.85, w: 5.8, h: 0.5, fontSize: 10, lineSpacingMultiple: 1.15 });
placeholder(b, "QR", W - M - 1.0, by + 0.25, 1.0, 1.0, { fill: { color: C.white } });
text(b, "無料相談を予約", { x: W - M - 1.3, y: by + 1.3, w: 1.6, h: 0.22, fontSize: 8.5, bold: true, color: C.white, align: "center" });

pres.writeFile({ fileName: __dirname + "/flyer.pptx" }).then((p) => console.log("wrote", p));
