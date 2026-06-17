import os
import re
from fpdf import FPDF

def preprocess_markdown(text):
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        stripped_line = line.strip()
        # Match bullet lists
        bullet_match = re.match(r'^[*+-]\s+(.*)$', stripped_line)
        # Match headers
        header_match = re.match(r'^#+\s+(.*)$', stripped_line)
        
        if bullet_match:
            content = bullet_match.group(1)
            new_lines.append(f"• {content}")
        elif header_match:
            content = header_match.group(1).strip()
            # Strip existing bold markers to prevent double-bolding
            content = content.replace('**', '').replace('__', '')
            new_lines.append(f"**{content}**")
        else:
            new_lines.append(stripped_line)
            
    return '\n'.join(new_lines)


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
            
            # Write Body (Response Text)
            preprocessed_response = preprocess_markdown(response_text)
            pdf.set_font("LiberationSans", style="", size=11)
            pdf.set_fallback_fonts(["DroidSansFallback"])
            pdf.multi_cell(w=0, text=preprocessed_response, markdown=True, align="L")
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
            "response_text": "Response 1 with **bold**.",
            "sources": [{"title": "Source 1", "url": "http://example.com/1"}]
        },
        {
            "query": "Test Query 2",
            "response_text": "Response 2 with *italic*.",
            "sources": [{"title": "Source 2", "url": None}]
        }
    ]
    generate_pdf_report(test_results, "test_report_multi.pdf")

