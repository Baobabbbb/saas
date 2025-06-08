import jsPDF from 'jspdf';

// Fonction pour charger une image et obtenir son dataURL
async function fetchImageInfo(url) {
  return new Promise((resolve, reject) => {
    const img = new window.Image();
    img.crossOrigin = "Anonymous";
    img.onload = function () {
      // Conversion en dataURL
      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      const dataUrl = canvas.toDataURL('image/png');
      resolve({ width: img.width, height: img.height, dataUrl });
    };
    img.onerror = reject;
    img.src = url;
  });
}

// Utilitaire pour un nom de fichier PDF safe
function getSafeFilename(str) {
  return String(str)
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "") // accents
    .replace(/[^a-z0-9]/gi, "_")
    .replace(/_+/g, "_")
    .replace(/^_|_$/g, "")
    .toLowerCase();
}

export async function downloadComicAsPDF(pages, title = 'bande-dessinee') {
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'px',
    format: [2048, 2048], // 📐 format carré, très haute résolution
  });

  const margin = 40;
  const cellSize = (2048 - margin * 2) / 2; // 2x2 grille

  // PRÉCHARGE toutes les images AVANT la création du PDF :
  const imgInfos = await Promise.all(
    pages.map(async (url) => {
      try {
        return await fetchImageInfo(url);
      } catch (e) {
        console.warn("Erreur chargement image pour le PDF :", url, e);
        return null;
      }
    })
  );

  let pageCount = 0;
  for (let i = 0; i < imgInfos.length; i++) {
    if (!imgInfos[i]) continue; // saute si image non chargée
    if (pageCount > 0 && pageCount % 4 === 0) pdf.addPage();

    const { dataUrl } = imgInfos[i];
    const position = pageCount % 4;
    const row = Math.floor(position / 2);
    const col = position % 2;

    const x = margin + col * cellSize;
    const y = margin + row * cellSize;

    pdf.addImage(dataUrl, 'PNG', x, y, cellSize, cellSize);
    pageCount++;
  }

  pdf.save(`${getSafeFilename(title)}.pdf`);
}
