import re
import markdown

def preprocess_markdown(text):
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        stripped_line = line.strip()
        bullet_match = re.match(r'^[*+-]\s+(.*)$', stripped_line)
        number_match = re.match(r'^(\d+)\.\s+(.*)$', stripped_line)
        
        if bullet_match:
            content = bullet_match.group(1)
            new_lines.append(f"• {content} <br>")
        elif number_match:
            num = number_match.group(1)
            content = number_match.group(2)
            new_lines.append(f"{num}\\. {content} <br>")
        else:
            new_lines.append(stripped_line)
            
    return '\n'.join(new_lines)

text = """
从济州国际机场前往牛岛，您需要先从机场到达城山浦港（Seongsan Port），然后搭乘渡轮前往牛岛。以下是具体的交通方式：

### **公共交通**

乘坐公共交通工具是从机场到牛岛的便捷选择。

*   **巴士 + 渡轮:**
    1.  **巴士**: 您可以从济州国际机场 乘坐巴士前往城山浦港。机场和港口均设有巴士站。具体的巴士线路号码和时刻表建议您在机场的咨询台查询，以获取最准确的信息。
    2.  **渡轮**: 到达城山浦港后，您可以在客运码头 乘坐渡轮前往牛岛。渡轮会抵达牛岛的两个港口之一：牛岛天进港（Udo Cheonjin port） 或下牛木洞港（Haumokdong Port）。由于未能查询到具体的渡轮班次和末班船时间，建议您在出发前或抵达港口后，直接在售票处确认时刻表。

### **自驾**

如果您选择租车自驾，路线同样是先到城山港再乘船。

*   **驾车 + 渡轮:**
    1.  **驾车**: 从济州国际机场 驾车前往城山浦港综合客运码头。
    2.  **关于车辆上岛**: 请注意，济州岛对于租赁汽车进入牛岛有相关限制。岛上有电动汽车租赁服务，通常鼓励游客在岛上租用小型交通工具游览，而不是将租来的汽车带上渡轮。建议您提前向租车公司或港口确认最新的车辆上岛政策。
    3.  **渡轮**: 将车停在城山港停车场后，乘坐渡轮前往牛岛的天进港 或下牛木洞港。

**总结建议:**
无论是选择公共交通还是自驾，都需要在城山浦港换乘渡轮。由于巴士和渡轮的时刻表可能会有变动，最稳妥的方式是抵达济州岛后，在机场或港口获取最新的时间信息。考虑到车辆上岛的限制，对于大多数游客而言，乘坐公共巴士到达港口，再换乘渡轮可能是更方便的选择。
"""

preprocessed = preprocess_markdown(text)
print("--- Preprocessed ---")
print(preprocessed)
print("--- HTML ---")
print(markdown.markdown(preprocessed))
