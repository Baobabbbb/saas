// Utilitaires pour générer des PDFs de bandes dessinées

import { jsPDF } from 'jspdf';

/**
 * Télécharge une bande dessinée au format PDF
 * @param {Array} imageUrls - URLs des pages de la BD
 * @param {string} filename - Nom du fichier PDF
 */
export const downloadComicAsPDF = async (imageUrls, filename = 'comic') => {
  try {
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    
    for (let i = 0; i < imageUrls.length; i++) {
      const imageUrl = imageUrls[i];
      
      try {
        // Charger l'image
        const img = new Image();
        img.crossOrigin = 'anonymous';
        
        await new Promise((resolve, reject) => {
          img.onload = resolve;
          img.onerror = reject;
          img.src = imageUrl;
        });
        
        // Calculer les dimensions pour ajuster à la page
        const imgWidth = img.width;
        const imgHeight = img.height;
        const ratio = Math.min(pageWidth / imgWidth, pageHeight / imgHeight);
        
        const scaledWidth = imgWidth * ratio;
        const scaledHeight = imgHeight * ratio;
        
        // Centrer l'image sur la page
        const x = (pageWidth - scaledWidth) / 2;
        const y = (pageHeight - scaledHeight) / 2;
        
        // Ajouter une nouvelle page (sauf pour la première)
        if (i > 0) {
          pdf.addPage();
        }
        
        // Ajouter l'image au PDF
        pdf.addImage(img, 'PNG', x, y, scaledWidth, scaledHeight);
        
      } catch (error) {
        console.error(`Erreur lors du chargement de l'image ${i + 1}:`, error);
        
        // Ajouter une page d'erreur
        if (i > 0) {
          pdf.addPage();
        }
        
        pdf.setFontSize(16);
        pdf.text(`Erreur lors du chargement de la page ${i + 1}`, 20, 50);
      }
    }
    
    // Télécharger le PDF
    const safeFilename = filename.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    pdf.save(`${safeFilename}.pdf`);
    
  } catch (error) {
    console.error('Erreur lors de la génération du PDF:', error);
    alert('Erreur lors de la génération du PDF. Veuillez réessayer.');
  }
};

export default downloadComicAsPDF;
