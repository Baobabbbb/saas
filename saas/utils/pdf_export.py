from reportlab.pdfgen import canvas

def export_to_pdf(image_paths, output="static/final_comic.pdf"):
    c = canvas.Canvas(output)
    for path in image_paths:
        c.drawImage(path, 0, 0, width=595, height=842)  # A4
        c.showPage()
    c.save()
