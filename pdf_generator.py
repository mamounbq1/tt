from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle

def generate_pdf(data, filename):
    # Create PDF document in landscape orientation
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(A4),
        initialFontName='Helvetica',
        initialFontSize=10
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Calculate optimal column widths
    page_width = landscape(A4)[0] - (doc.leftMargin + doc.rightMargin)
    time_col_width = page_width * 0.15  # 15% for time column
    other_col_width = (page_width - time_col_width) / 5  # Remaining space divided among 5 days
    
    # Prepare table data with proper styling
    table_data = []
    
    # Add header row
    header_row = ["Horaire", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    table_data.append([Paragraph(cell, styles['Heading2']) for cell in header_row])
    
    # Process schedule data
    for row in data:
        styled_row = []
        for i, cell in enumerate(row):
            if i == 0:  # Time column
                styled_row.append(Paragraph(cell, styles['Heading3']))
            elif "Pause Déjeuner" in cell:  # Lunch break styling
                styled_row.append(Paragraph(cell, ParagraphStyle(
                    'LunchBreak',
                    parent=styles['Normal'],
                    textColor=colors.gray,
                    fontSize=10,
                    alignment=1
                )))
            else:
                styled_row.append(Paragraph(cell if cell else "-", styles['Normal']))
        table_data.append(styled_row)
    
    # Create table with calculated column widths
    table = Table(table_data, 
                 colWidths=[time_col_width] + [other_col_width] * 5,
                 rowHeights=[40] + [30] * (len(data)))
    
    # Define table style
    table.setStyle(TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Time column styling
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#34495E')),
        ('TEXTCOLOR', (0, 1), (0, -1), colors.white),
        
        # Lunch break row styling
        ('BACKGROUND', (0, len(data) // 2), 
         (-1, len(data) // 2), colors.HexColor('#ECF0F1')),
        
        # General table styling
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    # Build document
    title = Paragraph("Emploi du Temps", title_style)
    doc.build([title, table])