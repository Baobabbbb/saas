import jsPDF from 'jspdf';

export async function downloadComicAsPDF(pages, title = 'bande-dessinee') {
  // Dimensions originales des images
  const imageWidth = 1660;
  const imageHeight = 1260;
  const imageRatio = imageWidth / imageHeight;

  // PDF adapté à la largeur standard (210mm) et au bon ratio
  const pdfWidth = 210; // mm
  const pdfHeight = pdfWidth / imageRatio; // ≈ 159.6 mm

  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: [pdfWidth, pdfHeight],
  });

  for (let i = 0; i < pages.length; i++) {
    const pageUrl = `http://127.0.0.1:8000${pages[i]}`;
    const img = await loadImage(pageUrl);

    if (i > 0) pdf.addPage();
    pdf.addImage(img, 'PNG', 0, 0, pdfWidth, pdfHeight);
  }

  pdf.save(`${getSafeFilename(title)}.pdf`);
}

function loadImage(url) {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => resolve(img);
    img.src = url;
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
