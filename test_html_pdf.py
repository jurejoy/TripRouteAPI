import markdown
from fpdf import FPDF

def test_html_pdf():
    # Markdown content with Chinese
    md_content = """
# 东京成田机场去佐渡岛交通方案

以下是从东京成田机场到佐渡岛的交通方案，分为**自驾**和**公共交通**两种方式。

## 公共交通方式
1.  **成田机场 -> 东京站/上野站**: 乘坐 *JR成田特快* (N'EX) 约 1 小时。
2.  **东京站/上野站 -> 新潟站**: 换乘 *上越新干线* 约 2 小时。
3.  **新潟站 -> 新潟港**: 乘坐巴士约 15-20 分钟。
4.  **新潟港 -> 两津港 (佐渡岛)**: 乘坐 *佐渡汽船*。
    *   高速船 (Jetfoil): 约 65 分钟。
    *   渡轮 (Car Ferry): 约 2.5 小时。

## 自驾方式
*   从成田机场租车，经高速公路前往新潟港（约 4-5 小时）。
*   在新潟港将车辆开上渡轮前往两津港。

[佐渡汽船官网](https://www.sadokisen.co.jp/)
"""

    # Convert Markdown to HTML
    html_content = markdown.markdown(md_content)
    print("Generated HTML:")
    print(html_content)
    print("----------------")

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Add CJK font
    font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    pdf.add_font("NotoSansCJK", style="", fname=font_path, collection_font_number=0)
    pdf.set_font("NotoSansCJK", size=12)
    
    # We also need bold version of the font for <b> or <strong> tags
    # NotoSansCJK-Bold.ttc should be at the same location
    bold_font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    pdf.add_font("NotoSansCJK", style="B", fname=bold_font_path, collection_font_number=0)
    
    # And maybe Italic? Noto Sans CJK doesn't have native italic, we might need to simulate or use regular for italic too.
    # fpdf2 might warning if 'I' style is missing but used in HTML.
    # Let's map regular to 'I' as well just in case, or see if it handles it.
    # Actually, we can add it with style="I" pointing to regular font.
    pdf.add_font("NotoSansCJK", style="I", fname=font_path, collection_font_number=0)

    # Set as default font
    pdf.set_font("NotoSansCJK", size=11)

    try:
        # write_html expects the font to be set.
        # It will use the current font family.
        # We need to make sure we set the font before calling write_html.
        # Also, fpdf2 write_html uses the font that is set.
        # If we use tags like H1, it might try to switch styles (e.g. Bold).
        # So having 'B' style registered is important.
        pdf.write_html(html_content)
        pdf.output("test_html.pdf")
        print("PDF generated: test_html.pdf")
    except Exception as e:
        print(f"Failed to write HTML to PDF: {e}")

if __name__ == "__main__":
    test_html_pdf()
