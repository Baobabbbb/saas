import jsPDF from 'jspdf';

export async function downloadComicAsPDF(pages, title = 'bande-dessinee') {
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'px',
    format: [2048, 2048], // 📐 format carré, très haute résolution
  });

  const margin = 40;
  const cellSize = (2048 - margin * 2) / 2; // 2x2 grille

  for (let i = 0; i < pages.length; i++) {
    if (i > 0 && i % 4 === 0) pdf.addPage(); // nouvelle planche toutes les 4 images

    const { dataUrl } = await fetchImageInfo(pages[i]);

    const position = i % 4;
    const row = Math.floor(position / 2);
    const col = position % 2;

    const x = margin + col * cellSize;
    const y = margin + row * cellSize;

    pdf.addImage(dataUrl, 'PNG', x, y, cellSize, cellSize);
  }

  pdf.save(`${getSafeFilename(title)}.pdf`);
}
