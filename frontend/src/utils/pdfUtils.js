// Utilitaires pour générer des PDFs de bandes dessinées

import { jsPDF } from 'jspdf';
import { getSafeFilename, addHerbbieSuffix } from './coloringPdfUtils';

/**
 * Télécharge une bande dessinée au format PDF
 * @param {Array} imageUrls - URLs des pages de la BD
 * @param {string} filename - Nom du fichier PDF
 */
export const downloadComicAsPDF = async (imageUrls, filename = 'comic') => {
  try {
    // Utiliser 'px' comme unité pour être cohérent avec les coloriages
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
    
    // Fonction pour charger une image et obtenir son dataURL
    const fetchImageInfo = (url) => {
      return new Promise((resolve, reject) => {
        const img = new window.Image();
        img.crossOrigin = "Anonymous";
        img.onload = function () {
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
    };
    
    // Précharger toutes les images
    const imgInfos = await Promise.all(
      imageUrls.map(async (imageUrl) => {
        try {
          return await fetchImageInfo(imageUrl);
        } catch (e) {
          console.warn("Erreur chargement image BD pour le PDF :", imageUrl, e);
          return null;
        }
      })
    );
    
    let isFirstPage = true;
    
    for (let i = 0; i < imgInfos.length; i++) {
      if (!imgInfos[i]) continue;
      
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
      
      // Ajouter l'image au PDF
      pdf.addImage(dataUrl, 'PNG', x, y, finalWidth, finalHeight);
      
      // 🏷️ Watermark "Créé avec HERBBIE" en bas à gauche (après l'image pour être au-dessus)
      pdf.setFontSize(8);
      pdf.setTextColor(107, 78, 255); // #6B4EFF - Violet HERBBIE
      pdf.text("Créé avec HERBBIE", 15, pageHeight - 10, { align: "left" });
        
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
    const safeFilename = getSafeFilename(filename, 'comic');
    pdf.save(addHerbbieSuffix(safeFilename, 'pdf'));
    
  } catch (error) {
    console.error('Erreur lors de la génération du PDF:', error);
    alert('Erreur lors de la génération du PDF. Veuillez réessayer.');
  }
};

export default downloadComicAsPDF;
