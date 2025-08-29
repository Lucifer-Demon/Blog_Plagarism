from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.flowables import HRFlowable
from io import BytesIO
import re
import math
from nltk.corpus import stopwords

def compute_similarity_with_details(text1, text2):
    stop_words = set(stopwords.words("english"))
    word_pattern = r"\b\w+\b"

    words1 = [w for w in re.findall(word_pattern, text1.lower()) if w not in stop_words]
    words2 = [w for w in re.findall(word_pattern, text2.lower()) if w not in stop_words]

    total_words = len(set(words1 + words2))
    overlapping_words = len(set(words1) & set(words2))

    all_words = list(set(words1 + words2))
    vec1 = [words1.count(w) for w in all_words]
    vec2 = [words2.count(w) for w in all_words]

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))

    similarity = (dot_product / (magnitude1 * magnitude2)) * 100 if magnitude1 and magnitude2 else 0.0
    return round(similarity, 2), total_words, overlapping_words

def generate_plagiarism_report_pdf(text, plagiarized_indices, similarity_percent):
    """
    Generate a PDF report for plagiarism results.
    
    Arguments:
    - text: the full text string checked.
    - plagiarized_indices: list of tuples (start_index, end_index) for plagiarized parts.
    - similarity_percent: overall plagiarism percentage.
    
    Returns:
    - PDF file bytes.
    """

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    # Custom style for highlighted plagiarized text (red color)
    highlight_style = ParagraphStyle(
        'highlight',
        parent=normal_style,
        textColor=colors.red,
        backColor=colors.yellow,
    )

    story = []

    # Title
    story.append(Paragraph("Plagiarism Report", styles['Title']))
    story.append(Spacer(1, 12))

    # Similarity percent info
    story.append(Paragraph(f"Similarity: <b>{similarity_percent}%</b>", styles['Heading2']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 12))

    # Prepare the text with highlighted plagiarized parts
    # We'll split text into segments, some normal, some highlighted

    last_index = 0
    segments = []

    for start, end in plagiarized_indices:
        if last_index < start:
            # Add normal text before the plagiarized part
            segments.append((text[last_index:start], normal_style))
        # Add highlighted plagiarized part
        segments.append((text[start:end], highlight_style))
        last_index = end

    # Add any remaining normal text after last plagiarized segment
    if last_index < len(text):
        segments.append((text[last_index:], normal_style))

    # Combine segments as Paragraphs, but since ReportLab Paragraph needs HTML-like tags,
    # We'll join segments as a single string with <font> tags for color

    combined_html = ""
    for segment_text, style in segments:
        if style == highlight_style:
            combined_html += f'<font color="red" backcolor="yellow">{segment_text}</font>'
        else:
            combined_html += segment_text

    # Add combined paragraph
    story.append(Paragraph(combined_html, normal_style))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
