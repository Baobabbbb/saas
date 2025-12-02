import { jsPDF } from 'jspdf';

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

// Utilitaire pour un nom de fichier safe et cohérent
export function getSafeFilename(str, contentType = '') {
  if (!str || str.trim() === '') {
    // Noms par défaut selon le type de contenu
    const defaults = {
      'coloriage': 'coloriage',
      'comic': 'bande_dessinee',
      'comptine': 'comptine',
      'histoire': 'histoire',
      'animation': 'animation'
    };
    str = defaults[contentType] || 'creation';
  }

  return String(str)
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "") // accents
    .replace(/[^a-z0-9]/gi, "_")
    .replace(/_+/g, "_")
    .replace(/^_|_$/g, "")
    .toLowerCase();
}

// Fonction helper pour ajouter "_herbbie" avant l'extension
export function addHerbbieSuffix(filename, extension) {
  // Si le filename contient déjà l'extension, on la retire d'abord
  const baseName = filename.replace(new RegExp(`\\.${extension}$`, 'i'), '');
  return `${baseName}_herbbie.${extension}`;
}

export async function downloadColoringAsPDF(images, title = 'coloriages') {
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'px',
    format: 'a4',
  });

  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 40;
  const imageWidth = pageWidth - 2 * margin;
  const imageHeight = pageHeight - 2 * margin;
  // PRÉCHARGE toutes les images AVANT la création du PDF :
  const imgInfos = await Promise.all(
    images.map(async (imageItem) => {
      try {
        const url = imageItem.image_url || imageItem;
        return await fetchImageInfo(url);
      } catch (e) {
        console.warn("Erreur chargement image pour le PDF :", imageItem, e);
        return null;
      }
    })
  );

  let isFirstPage = true;
  
  for (let i = 0; i < imgInfos.length; i++) {
    if (!imgInfos[i]) continue; // saute si image non chargée
    
    if (!isFirstPage) {
      pdf.addPage();
    }
    isFirstPage = false;

    const { dataUrl, width, height } = imgInfos[i];
    
    // Calcul des dimensions pour garder les proportions
    const aspectRatio = width / height;
    let finalWidth = imageWidth;
    let finalHeight = imageWidth / aspectRatio;
    
    if (finalHeight > imageHeight) {
      finalHeight = imageHeight;
      finalWidth = imageHeight * aspectRatio;
    }
    
    // Centrage de l'image
    const x = (pageWidth - finalWidth) / 2;
    const y = (pageHeight - finalHeight) / 2;

    pdf.addImage(dataUrl, 'PNG', x, y, finalWidth, finalHeight);
  }

  pdf.save(addHerbbieSuffix(getSafeFilename(title), 'pdf'));
}
