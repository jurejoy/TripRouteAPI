import os
import re
from fpdf import FPDF

def preprocess_normal_text(text):
    """Simplistic preprocessing for normal text, mainly converting markdown bullets to unicode bullets."""
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        stripped_line = line.strip()
        # Match bullet lists
        bullet_match = re.match(r'^[*+-]\s+(.*)$', stripped_line)
        if bullet_match:
            content = bullet_match.group(1)
            new_lines.append(f"• {content}")
        else:
            new_lines.append(stripped_line)
            
    return '\n'.join(new_lines)

def parse_and_write_markdown(pdf, text):
    """Parses markdown text and writes it to the PDF block by block to support different styles."""
    lines = text.split('\n')
    in_code_block = False
    code_lines = []
    normal_lines = []
    
    def flush_normal_paragraphs():
        nonlocal normal_lines
        if normal_lines:
            paragraph_text = '\n'.join(normal_lines)
            # Check if it's just empty lines
            if paragraph_text.strip():
                preprocessed = preprocess_normal_text(paragraph_text)
                pdf.set_font("LiberationSans", style="", size=11)
                pdf.set_fallback_fonts(["DroidSansFallback"])
                # Enable markdown for bold/italic/links
                pdf.multi_cell(w=0, text=preprocessed, markdown=True, align="L")
                pdf.ln(2)
            else:
                # If it's just empty lines, we can just add some vertical space
                pdf.ln(2)
            normal_lines = []

    def flush_code_block():
        nonlocal code_lines
        if code_lines:
            code_text = '\n'.join(code_lines)
            
            # Save current font and style to restore later
            current_font = pdf.font_family
            current_style = pdf.font_style
            current_size = pdf.font_size_pt
            
            # Use registered monospace font if available, otherwise fallback to Courier
            code_font = getattr(pdf, "code_font", "Courier")
            pdf.set_font(code_font, style="", size=9.5)
            pdf.set_fallback_fonts(["DroidSansFallback"])
            
            # Set light gray background
            pdf.set_fill_color(240, 240, 240)
            
            # Draw a light gray box with the code
            pdf.multi_cell(w=0, text=code_text, fill=True, align="L")
            pdf.ln(3)
            
            # Restore previous font and reset fill
            pdf.set_font(current_font, style=current_style, size=current_size)
            pdf.set_fill_color(255, 255, 255)
            code_lines = []

    for line in lines:
        # Detect code block marker
        if line.strip().startswith("```"):
            if in_code_block:
                flush_code_block()
                in_code_block = False
            else:
                flush_normal_paragraphs()
                in_code_block = True
        elif in_code_block:
            code_lines.append(line)
        else:
            # Detect headers
            header_match = re.match(r'^#+\s+(.*)$', line.strip())
            if header_match:
                flush_normal_paragraphs()
                header_text = header_match.group(1).strip()
                # Strip bold markers from header text
                header_text = header_text.replace('**', '').replace('__', '')
                
                # Determine header level
                level = len(re.match(r'^#+', line.strip()).group(0))
                size = 14 if level == 1 else (13 if level == 2 else 12)
                
                pdf.set_font("LiberationSans", style="B", size=size)
                pdf.set_fallback_fonts(["DroidSansFallback"])
                pdf.multi_cell(w=0, text=header_text, align="L")
                pdf.ln(3)
            else:
                normal_lines.append(line)
                
    # Flush any remaining blocks
    flush_normal_paragraphs()
    flush_code_block()


def generate_pdf_report(results, output_filename="report.pdf"):
    """
    Generates a PDF report from a list of Gemini responses and grounding sources.
    Each section is written on a new page.
    """
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Configure Fonts
    liberation_dir = "/usr/share/fonts/truetype/liberation"
    droid_font = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
    
    liberation_regular = os.path.join(liberation_dir, "LiberationSans-Regular.ttf")
    liberation_bold = os.path.join(liberation_dir, "LiberationSans-Bold.ttf")
    liberation_italic = os.path.join(liberation_dir, "LiberationSans-Italic.ttf")
    liberation_bold_italic = os.path.join(liberation_dir, "LiberationSans-BoldItalic.ttf")

    liberation_mono_regular = os.path.join(liberation_dir, "LiberationMono-Regular.ttf")
    liberation_mono_bold = os.path.join(liberation_dir, "LiberationMono-Bold.ttf")
    liberation_mono_italic = os.path.join(liberation_dir, "LiberationMono-Italic.ttf")
    liberation_mono_bold_italic = os.path.join(liberation_dir, "LiberationMono-BoldItalic.ttf")

    try:
        # Register DroidSansFallback for all styles
        pdf.add_font("DroidSansFallback", style="", fname=droid_font)
        pdf.add_font("DroidSansFallback", style="B", fname=droid_font)
        pdf.add_font("DroidSansFallback", style="I", fname=droid_font)
        pdf.add_font("DroidSansFallback", style="BI", fname=droid_font)
        
        # Register LiberationSans with proper styles
        pdf.add_font("LiberationSans", style="", fname=liberation_regular)
        if os.path.exists(liberation_bold):
            pdf.add_font("LiberationSans", style="B", fname=liberation_bold)
        if os.path.exists(liberation_italic):
            pdf.add_font("LiberationSans", style="I", fname=liberation_italic)
        if os.path.exists(liberation_bold_italic):
            pdf.add_font("LiberationSans", style="BI", fname=liberation_bold_italic)
            
        # Register LiberationMono (Monospace for code blocks)
        pdf.code_font = "Courier" # Default fallback
        if os.path.exists(liberation_mono_regular):
            pdf.add_font("LiberationMono", style="", fname=liberation_mono_regular)
            pdf.code_font = "LiberationMono"
            if os.path.exists(liberation_mono_bold):
                pdf.add_font("LiberationMono", style="B", fname=liberation_mono_bold)
            if os.path.exists(liberation_mono_italic):
                pdf.add_font("LiberationMono", style="I", fname=liberation_mono_italic)
            if os.path.exists(liberation_mono_bold_italic):
                pdf.add_font("LiberationMono", style="BI", fname=liberation_mono_bold_italic)
            
    except Exception as e:
        print(f"Error configuring fonts: {e}")
        return False

    # Enable markdown link styling
    pdf.MARKDOWN_LINK_COLOR = (0, 0, 255)
    pdf.MARKDOWN_LINK_UNDERLINE = True

    try:
        pdf.set_margins(15, 15, 15)
        
        # Write Main Title
        pdf.set_font("LiberationSans", style="B", size=16)
        pdf.set_fallback_fonts(["DroidSansFallback"])
        pdf.multi_cell(w=0, text="Research Report", align="L")
        pdf.ln(10)
        
        for i, result in enumerate(results):
            query = result.get('query')
            response_text = result.get('response_text')
            sources = result.get('sources') or []
            
            # Write Section Header
            pdf.set_font("LiberationSans", style="B", size=14)
            pdf.set_fallback_fonts(["DroidSansFallback"])
            pdf.multi_cell(w=0, text=f"Section {i+1}: {query}", align="L")
            pdf.ln(5)
            
            # Write Body (Response Text parsed as markdown blocks)
            parse_and_write_markdown(pdf, response_text)
            pdf.ln(5)
            
            # Write Sources
            if sources:
                pdf.set_font("LiberationSans", style="B", size=12)
                pdf.set_fallback_fonts(["DroidSansFallback"])
                pdf.multi_cell(w=0, text="Sources & Attributions", align="L")
                pdf.ln(2)
                
                sources_md = []
                for source in sources:
                    title = source.get('title') or "Map Link"
                    url = source.get('url')
                    if url:
                        sources_md.append(f"• [{title}]({url})")
                    else:
                        sources_md.append(f"• {title}")
                
                pdf.set_font("LiberationSans", style="", size=11)
                pdf.set_fallback_fonts(["DroidSansFallback"])
                pdf.multi_cell(w=0, text="\n".join(sources_md), markdown=True, align="L")
                
            # Add page break for next section
            if i < len(results) - 1:
                pdf.add_page()
                
        pdf.output(output_filename)
        print(f"Successfully generated PDF report: {output_filename}")
        return True
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False

# Quick test if run directly
if __name__ == "__main__":
    test_results = [
        {
            "query": "Test Query 1",
            "response_text": """This is a normal paragraph with **bold** text.
            
### Header 3
Here is a code block:
```python
def hello():
    print("Hello World")
    # Chinese comment: 中文注释
```
And another paragraph after the code block.""",
            "sources": [{"title": "Source 1", "url": "http://example.com/1"}]
        }
    ]
    generate_pdf_report(test_results, "test_report_generator_complex.pdf")
