from reportlab.lib import colors
from reportlab.lib.pagesizes import A4  # Portrait orientation by default
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
from datetime import datetime

def generate_grouped_schedule_table(data, styles, col_widths):
    """
    Generates a single table that groups schedule entries by class.
    Each class group starts with a merged row displaying the class name,
    followed by its schedule entries.
    
    The table columns are:
      1. Date (day and date)
      2. Slot Time
      3. Content
      4. Observation
    """
    table_data = []
    merge_rows = []  # To keep track of row indices where class names appear

    # Add a global header row.
    header = [
        Paragraph("<b>Date</b>", styles["Heading4"]),
        Paragraph("<b>Slot Time</b>", styles["Heading4"]),
        Paragraph("<b>Content</b>", styles["Heading4"]),
        Paragraph("<b>Observation</b>", styles["Heading4"])
    ]
    table_data.append(header)
    row_index = 1  # Header occupies row 0

    # Create a centered paragraph style for class names
    centered_style = ParagraphStyle(
        'CenteredStyle',
        parent=styles['Heading3'],
        alignment=1,  # 1 is for CENTER alignment
        spaceAfter=0,
        spaceBefore=0
    )

    # Process each class in the data dictionary.
    for class_name, entries in data.items():
        # Add a merged row for the class name with centered style
        class_row = [
            Paragraph(f"<b>{class_name}</b>", centered_style),
            '', '', ''
        ]
        table_data.append(class_row)
        merge_rows.append(row_index)
        row_index += 1

        # Add schedule entries for this class.
        for entry in entries:
            # Convert and format the date (assumed format: YYYY-MM-DD)
            dt = datetime.strptime(entry['date'], "%Y-%m-%d")
            formatted_date = dt.strftime("%A, %Y-%m-%d")
            date_cell = Paragraph(formatted_date, styles["Normal"])

            time_cell = Paragraph(entry['time'], styles["Normal"])
            content_cell = Paragraph(entry['content'], styles["Normal"])
            observation_cell = Paragraph(entry.get('observation', ''), styles["Normal"])

            table_data.append([date_cell, time_cell, content_cell, observation_cell])
            row_index += 1

    # Create the table with explicit alignment
    table = Table(table_data, colWidths=col_widths, hAlign="CENTER")

    # Build the table style.
    style_commands = [
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Global center alignment
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]
    
    # Style the header row.
    style_commands.extend([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d3d3d3')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER')
    ])
    
    # For each class row, merge all four columns and apply custom styling.
    for merge_row in merge_rows:
        style_commands.append(('SPAN', (0, merge_row), (3, merge_row)))
        style_commands.append(('BACKGROUND', (0, merge_row), (3, merge_row), colors.HexColor('#9fc5e8')))
        style_commands.append(('ALIGN', (0, merge_row), (3, merge_row), 'CENTER'))
        style_commands.append(('VALIGN', (0, merge_row), (3, merge_row), 'MIDDLE'))
        style_commands.append(('FONTNAME', (0, merge_row), (3, merge_row), 'Helvetica-Bold'))
        style_commands.append(('FONTSIZE', (0, merge_row), (3, merge_row), 8))
        style_commands.append(('TEXTCOLOR', (0, merge_row), (3, merge_row), colors.HexColor('#666666')))
        style_commands.append(('TOPPADDING', (0, merge_row), (3, merge_row), 6))
        style_commands.append(('BOTTOMPADDING', (0, merge_row), (3, merge_row), 6))
    
    table.setStyle(TableStyle(style_commands))
    return table

def generate_pdf_grouped(data, filename):
    """
    Generates a PDF with a single table grouping all class schedules.

    :param data: A dictionary where each key is a class name (e.g., "TCSF1")
                 and each value is a list of schedule entries. Each schedule entry is
                 a dictionary with the following keys:
                   - 'date': "YYYY-MM-DD"
                   - 'time': slot time (e.g., "08:00-09:30")
                   - 'content': description of the slot (e.g., "Mathematics")
                   - Optional: 'observation': additional remarks.
    :param filename: The output filename for the generated PDF.
    """
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,  # Portrait orientation
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Grouped Class Schedules"
    )
    styles = getSampleStyleSheet()
    story = []

    # Calculate available width and define column widths.
    page_width, _ = A4
    doc_width = page_width - (1.5 * cm + 1.5 * cm)
    # Define widths: Date: 25%, Slot Time: 20%, Content: 35%, Observation: 20%
    col_widths = [
        doc_width * 0.25,
        doc_width * 0.20,
        doc_width * 0.35,
        doc_width * 0.20
    ]

    # Generate the grouped schedule table.
    table = generate_grouped_schedule_table(data, styles, col_widths)
    story.append(table)
    doc.build(story)

if __name__ == "__main__":
    # Example data
    sample_data = {
        "TCSF1": [
            {
                "date": "2025-02-10",
                "time": "08:00-09:30",
                "content": "Mathematics",
                "observation": "Bring calculator"
            },
            {
                "date": "2025-02-11",
                "time": "09:45-11:15",
                "content": "Physics",
                "observation": ""
            },
            {
                "date": "2025-02-12",
                "time": "11:30-13:00",
                "content": "Chemistry",
                "observation": "Lab session"
            }
        ],
        "TCSF2": [
            {
                "date": "2025-02-10",
                "time": "08:00-09:30",
                "content": "Biology",
                "observation": ""
            },
            {
                "date": "2025-02-11",
                "time": "09:45-11:15",
                "content": "History",
                "observation": "Quiz at end"
            },
            {
                "date": "2025-02-12",
                "time": "11:30-13:00",
                "content": "Geography",
                "observation": ""
            }
        ]
    }

    output_filename = "grouped_class_schedules.pdf"
    generate_pdf_grouped(sample_data, output_filename)