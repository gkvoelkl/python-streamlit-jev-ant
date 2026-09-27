// Builds the Word document from the German chapters in `tutorial/`.
//
//     npm install docx        # once
//     node tools/build_tutorial.js
//
// The Markdown in tutorial/ is the source; `Ameisen-die-fragen.docx` is a
// product of it and is not edited by hand. Everything written here understands
// exactly the Markdown those chapters use — headings, paragraphs, fenced code,
// tables, bullet lists, block quotes, and inline `code`, **bold** and links.
// It is not a general converter and does not try to be.

const fs = require("node:fs");
const path = require("node:path");
const {
  AlignmentType,
  BorderStyle,
  Document,
  HeadingLevel,
  ImageRun,
  LevelFormat,
  Packer,
  Paragraph,
  ShadingType,
  Table,
  TableCell,
  TableRow,
  TextRun,
  WidthType,
} = require("docx");

const ROOT = path.join(__dirname, "..");
const CHAPTERS = path.join(ROOT, "tutorial");
const OUT = path.join(ROOT, "Ameisen-die-fragen.docx");

const MONO = "Consolas";
const CODE_BG = "F2F2F4";
const CODE_SIZE = 17; // half-points, so 8.5pt — listings are wide
const TEXT_WIDTH = 9360; // DXA, the printable width of an A4 page with 2.5cm margins

// --- pictures ------------------------------------------------------------

const TEXT_WIDTH_PX = 624; // the printable width in pixels at 96 dpi

function pngSize(data) {
  // The IHDR chunk is always first and always holds width and height as two
  // big-endian 32-bit numbers. Cheaper than a dependency for one fact.
  return { width: data.readUInt32BE(16), height: data.readUInt32BE(20) };
}

function picture(alt, src) {
  const file = path.join(CHAPTERS, src);
  if (!fs.existsSync(file)) {
    console.warn(`  ! missing picture: ${src}`);
    return new Paragraph({ children: runs(`[missing picture: ${src}]`) });
  }

  const data = fs.readFileSync(file);
  const { width, height } = pngSize(data);
  const scale = Math.min(1, TEXT_WIDTH_PX / width);

  return new Paragraph({
    children: [
      new ImageRun({
        data,
        type: "png",
        altText: { name: src, title: alt, description: alt },
        transformation: {
          width: Math.round(width * scale),
          height: Math.round(height * scale),
        },
      }),
    ],
    alignment: AlignmentType.CENTER,
    spacing: { before: 160, after: 80 },
  });
}

// --- inline: **bold**, *italic*, `code`, [text](url) ---------------------

function runs(text, base = {}) {
  const out = [];
  const pattern =
    /(\*\*[^*]+\*\*|\*[^*\n]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))/g;
  let last = 0;

  for (const match of text.matchAll(pattern)) {
    if (match.index > last) {
      out.push(new TextRun({ text: text.slice(last, match.index), ...base }));
    }
    const piece = match[0];

    if (piece.startsWith("**")) {
      out.push(new TextRun({ text: piece.slice(2, -2), bold: true, ...base }));
    } else if (piece.startsWith("*")) {
      out.push(new TextRun({ text: piece.slice(1, -1), italics: true, ...base }));
    } else if (piece.startsWith("`")) {
      out.push(
        new TextRun({
          text: piece.slice(1, -1),
          font: MONO,
          size: CODE_SIZE,
          shading: { type: ShadingType.CLEAR, fill: CODE_BG },
          ...base,
        }),
      );
    } else {
      // A link, kept as its text plus the address in brackets: a printed
      // tutorial is read on paper as often as on screen.
      const [, label, url] = piece.match(/\[([^\]]+)\]\(([^)]+)\)/);
      out.push(new TextRun({ text: label, ...base }));
      if (!url.startsWith("#")) {
        out.push(new TextRun({ text: ` (${url})`, size: 18, color: "6A6A72", ...base }));
      }
    }
    last = match.index + piece.length;
  }

  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}

// --- blocks --------------------------------------------------------------

function codeBlock(lines) {
  // One paragraph per line, with the shading carried by the paragraph so the
  // block reads as one grey field even where a line is empty.
  return lines.map(
    (line, index) =>
      new Paragraph({
        children: [new TextRun({ text: line || " ", font: MONO, size: CODE_SIZE })],
        shading: { type: ShadingType.CLEAR, fill: CODE_BG },
        spacing: {
          before: index === 0 ? 120 : 0,
          after: index === lines.length - 1 ? 160 : 0,
          line: 240,
        },
        indent: { left: 200, right: 200 },
        keepNext: index < lines.length - 1,
      }),
  );
}

function tableBlock(rows) {
  const cells = rows.map((row) =>
    row
      .replace(/^\||\|$/g, "")
      .split("|")
      .map((cell) => cell.trim()),
  );
  const [header, , ...body] = cells; // the second row is the ---|--- rule
  const columns = header.length;
  const width = Math.floor(TEXT_WIDTH / columns);
  const widths = Array(columns).fill(width);

  const row = (values, isHeader) =>
    new TableRow({
      tableHeader: isHeader,
      children: values.map(
        (value) =>
          new TableCell({
            width: { size: width, type: WidthType.DXA },
            shading: isHeader ? { type: ShadingType.CLEAR, fill: "EDEDF0" } : undefined,
            margins: { top: 60, bottom: 60, left: 120, right: 120 },
            children: [
              new Paragraph({
                children: runs(value, isHeader ? { bold: true } : {}),
                spacing: { before: 0, after: 0 },
              }),
            ],
          }),
      ),
    });

  return new Table({
    columnWidths: widths,
    width: { size: TEXT_WIDTH, type: WidthType.DXA },
    rows: [row(header, true), ...body.map((values) => row(values, false))],
  });
}

function convert(markdown) {
  const lines = markdown.split("\n");
  const blocks = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (!line.trim()) {
      i += 1;
      continue;
    }

    if (line.startsWith("```")) {
      const code = [];
      i += 1;
      while (i < lines.length && !lines[i].startsWith("```")) code.push(lines[i++]);
      i += 1;
      blocks.push(...codeBlock(code));
      continue;
    }

    if (line.startsWith("|")) {
      const rows = [];
      while (i < lines.length && lines[i].startsWith("|")) rows.push(lines[i++]);
      blocks.push(tableBlock(rows));
      blocks.push(new Paragraph({ text: "", spacing: { after: 120 } }));
      continue;
    }

    // A working note, not content. It is left out of the document and
    // reported on the console, so an unanswered one is noticed without
    // ending up in front of a reader.
    if (line.trimStart().startsWith("/*")) {
      const note = [];
      while (i < lines.length && !lines[i].includes("*/")) note.push(lines[i++]);
      note.push(lines[i++] ?? "");
      console.warn(`  ! open note: ${note.join(" ").replace(/\/\*|\*\//g, "").trim().slice(0, 70)}`);
      continue;
    }

    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      const level = [
        HeadingLevel.HEADING_1,
        HeadingLevel.HEADING_2,
        HeadingLevel.HEADING_3,
        HeadingLevel.HEADING_4,
      ][heading[1].length - 1];
      blocks.push(
        new Paragraph({
          children: runs(heading[2]),
          heading: level,
          spacing: { before: heading[1].length === 1 ? 480 : 320, after: 160 },
          keepNext: true,
        }),
      );
      i += 1;
      continue;
    }

    if (line.startsWith("---")) {
      blocks.push(
        new Paragraph({
          text: "",
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "C8C8CE" } },
          spacing: { before: 240, after: 240 },
        }),
      );
      i += 1;
      continue;
    }

    if (line.startsWith("> ")) {
      const quote = [];
      while (i < lines.length && lines[i].startsWith(">")) {
        quote.push(lines[i++].replace(/^>\s?/, ""));
      }
      blocks.push(
        new Paragraph({
          children: runs(quote.join(" ")),
          indent: { left: 340 },
          border: { left: { style: BorderStyle.SINGLE, size: 12, color: "B9B9C2", space: 12 } },
          spacing: { before: 120, after: 200 },
        }),
      );
      continue;
    }

    if (/^[*-]\s/.test(line)) {
      while (i < lines.length && (/^[*-]\s/.test(lines[i]) || /^\s{2,}\S/.test(lines[i]))) {
        // A wrapped bullet continues on the next line, indented.
        let item = lines[i++].replace(/^[*-]\s+/, "");
        while (i < lines.length && /^\s{2,}\S/.test(lines[i])) item += " " + lines[i++].trim();
        blocks.push(
          new Paragraph({
            children: runs(item),
            numbering: { reference: "bullets", level: 0 },
            spacing: { after: 80 },
          }),
        );
      }
      continue;
    }

    // An ordinary paragraph: everything up to the next empty line.
    const paragraph = [];
    const startsPicture = /^!\[/.test(lines[i]);
    while (
      i < lines.length &&
      lines[i].trim() &&
      !lines[i].startsWith("#") &&
      !lines[i].startsWith("|") &&
      !lines[i].startsWith("```") &&
      !lines[i].startsWith(">") &&
      !/^[*-]\s/.test(lines[i]) &&
      // A picture ends where its closing bracket is, whatever follows.
      !(paragraph.length && startsPicture && /\)\s*$/.test(paragraph.at(-1)))
    ) {
      paragraph.push(lines[i++].trim());
    }
    const text = paragraph.join(" ");

    // A picture stands alone in its paragraph; the alt text may run over
    // several lines, which is why this is matched after joining them.
    const image = text.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
    if (image) {
      blocks.push(picture(image[1].replace(/\s+/g, " "), image[2]));
      continue;
    }

    blocks.push(
      new Paragraph({
        children: runs(text),
        spacing: { after: 180, line: 300 },
        alignment: AlignmentType.JUSTIFIED,
      }),
    );
  }

  return blocks;
}

// --- the document --------------------------------------------------------

const files = fs
  .readdirSync(CHAPTERS)
  .filter((name) => name.endsWith(".md"))
  .sort();

const body = [];
files.forEach((name, index) => {
  if (index > 0) {
    body.push(new Paragraph({ children: [], pageBreakBefore: true }));
  }
  body.push(...convert(fs.readFileSync(path.join(CHAPTERS, name), "utf8")));
});

const document = new Document({
  creator: "gkvoelkl",
  title: "Ameisen, die fragen",
  description: "Ein Spiel in acht Schritten mit Python, Streamlit und TypeSafe Jev",
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 420, hanging: 220 } } },
          },
        ],
      },
    ],
  },
  styles: {
    default: {
      document: { run: { font: "Calibri", size: 22 } },
      heading1: { run: { font: "Calibri", size: 36, bold: true, color: "1A1A1E" } },
      heading2: { run: { font: "Calibri", size: 28, bold: true, color: "1A1A1E" } },
      heading3: { run: { font: "Calibri", size: 24, bold: true, color: "3A3A42" } },
      heading4: { run: { font: "Calibri", size: 22, bold: true, color: "3A3A42" } },
    },
  },
  sections: [
    {
      properties: { page: { margin: { top: 1418, bottom: 1418, left: 1418, right: 1418 } } },
      children: body,
    },
  ],
});

Packer.toBuffer(document).then((buffer) => {
  fs.writeFileSync(OUT, buffer);
  console.log(`${path.relative(ROOT, OUT)} — ${files.length} Kapitel, ${(buffer.length / 1024).toFixed(0)} KB`);
});
