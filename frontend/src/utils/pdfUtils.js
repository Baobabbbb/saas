import jsPDF from 'jspdf';

export async function downloadComicAsPDF(pages, title = 'bande-dessinee') {
  const dpi = 96;
  const pxToMm = (px) => (px / dpi) * 25.4;

  const first = await fetchImageInfo(pages[0]);
  const pdfWidth = pxToMm(first.width);
  const pdfHeight = pxToMm(first.height);

  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: [pdfWidth, pdfHeight],
  });

  for (let i = 0; i < pages.length; i++) {
    const { dataUrl, width, height } = await fetchImageInfo(pages[i]);
    if (i > 0) pdf.addPage([pxToMm(width), pxToMm(height)]);
    pdf.addImage(dataUrl, 'PNG', 0, 0, pxToMm(width), pxToMm(height));
  }

  pdf.save(`${getSafeFilename(title)}.pdf`);
}

async function fetchImageInfo(relativePath) {
  const url = `http://127.0.0.1:8000${relativePath}`;
  const res = await fetch(url);
  const blob = await res.blob();

  const img = await createImageFromBlob(blob);

  const canvas = document.createElement('canvas');
  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;

  const ctx = canvas.getContext('2d');
  ctx.drawImage(img, 0, 0);

  const dataUrl = canvas.toDataURL('image/png');
  return {
    width: img.naturalWidth,
    height: img.naturalHeight,
    dataUrl,
  };
}

function createImageFromBlob(blob) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.src = URL.createObjectURL(blob);
  });
}

function getSafeFilename(title) {
  return title
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/[^a-z0-9_]/g, '');
}
