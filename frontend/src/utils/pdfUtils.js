import jsPDF from 'jspdf';

export async function downloadComicAsPDF(pages, title = 'bande-dessinee') {
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  });

  for (let i = 0; i < pages.length; i++) {
    const pageUrl = `http://127.0.0.1:8000${pages[i]}`;
    const img = await loadImage(pageUrl);

    const width = pdf.internal.pageSize.getWidth();
    const height = pdf.internal.pageSize.getHeight();

    if (i > 0) pdf.addPage();
    pdf.addImage(img, 'PNG', 0, 0, width, height);
  }

  pdf.save(`${title.replace(/\s+/g, '_').toLowerCase()}.pdf`);
}

function loadImage(url) {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => resolve(img);
    img.src = url;
  });
}
