#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to convert the LPT markdown article to HTML
Preserves all text exactly as is, only adds HTML structure
"""

import re

def escape_html(text):
    """Escape HTML special characters but preserve structure"""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def process_inline_formatting(text):
    """Process bold, italic, and other inline formatting"""
    # Bold with **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic with *text*
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    # Italic with _text_
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    return text

def convert_markdown_to_html(md_file):
    """Convert markdown file to HTML sections"""
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    html_sections = []
    current_section = None
    current_content = []
    in_table = False
    table_rows = []
    figure_counter = 1

    # Mapping of image references
    image_map = {
        '[image1]': ('Figure1_Global_PL.png', 'Figure 1'),
        '[image2]': ('Figure1bis_Global_LY.png', 'Figure 1bis'),
        '[image3]': ('Figure2_Trajectoires_LP.png', 'Figure 2'),
        '[image4]': ('Figure2bis_Trajectoires_LY.png', 'Figure 2bis'),
        '[image5]': ('Figure3_Bootstrap_b.png', 'Figure 3'),
        '[image6]': ('Figure_C1_L_vs_P.png', 'Figure C1'),
        '[image7]': ('Figure_C1bis_Y_vs_L.png', 'Figure C1bis'),
        '[image8]': ('Figure_C2_Trajectories_LP.png', 'Figure C2'),
        '[image9]': ('Figure_C2bis_Trajectories_LY.png', 'Figure C2bis'),
        '[image10]': ('Figure_D1_AI_Scaled.png', 'Figure D1'),
        '[image11]': ('Figure_D1bis_AI_Scaled.png', 'Figure D1bis'),
    }

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # Skip title and author (handled separately)
        if i < 10 and (line.startswith('# **LPT') or line == 'Djamchid Dalili' or line == '---'):
            i += 1
            continue

        # Handle headers
        if line.startswith('# '):
            # Close previous section
            if current_section:
                html_sections.append({
                    'id': current_section['id'],
                    'title': current_section['title'],
                    'level': current_section['level'],
                    'content': '\n'.join(current_content)
                })

            # Start new section
            title = line.lstrip('#').strip()
            title = re.sub(r'^\*\*(.+?)\*\*$', r'\1', title)  # Remove ** wrapper
            section_id = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            current_section = {'id': section_id, 'title': title, 'level': 1}
            current_content = []

        elif line.startswith('## '):
            if current_section:
                html_sections.append({
                    'id': current_section['id'],
                    'title': current_section['title'],
                    'level': current_section['level'],
                    'content': '\n'.join(current_content)
                })

            title = line.lstrip('#').strip()
            title = re.sub(r'^\*\*(.+?)\*\*$', r'\1', title)
            section_id = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            current_section = {'id': section_id, 'title': title, 'level': 2}
            current_content = []

        elif line.startswith('### '):
            title = line.lstrip('#').strip()
            title = re.sub(r'^\*\*(.+?)\*\*$', r'\1', title)
            current_content.append(f'<h3>{process_inline_formatting(title)}</h3>')

        elif line.startswith('#### '):
            title = line.lstrip('#').strip()
            title = re.sub(r'^\*\*(.+?)\*\*$', r'\1', title)
            current_content.append(f'<h4>{process_inline_formatting(title)}</h4>')

        # Handle tables
        elif line.startswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(line)

        elif in_table and not line.startswith('|'):
            # End of table
            current_content.append(convert_table(table_rows))
            table_rows = []
            in_table = False
            # Process current line after table
            if line.strip():
                if line.startswith('**![]'):
                    # Image reference
                    current_content.append(f'<p class="image-placeholder">{line}</p>')
                else:
                    current_content.append(f'<p>{process_inline_formatting(line)}</p>')

        # Handle image references
        elif '**![][image' in line or '*![][image' in line:
            # Extract image reference
            match = re.search(r'\[image(\d+)\]', line)
            if match:
                img_key = f'[image{match.group(1)}]'
                if img_key in image_map:
                    img_file, img_caption = image_map[img_key]
                    # Check if next lines contain caption
                    caption = ''
                    j = i + 1
                    while j < len(lines) and lines[j].strip() and not lines[j].startswith('#'):
                        caption += lines[j].strip() + ' '
                        j += 1

                    current_content.append(f'''
<figure class="figure" id="figure{match.group(1)}">
    <img src="{img_file}" alt="{img_caption}" onclick="zoomImage(this)">
    <figcaption>{process_inline_formatting(caption.strip())}</figcaption>
</figure>
''')
                    i = j - 1

        # Handle regular paragraphs
        elif line.strip() and not line.startswith('---'):
            # Check for special formatting
            if line.startswith('*(Voir Annexe'):
                current_content.append(f'<p class="annex-ref">{process_inline_formatting(line)}</p>')
            else:
                current_content.append(f'<p>{process_inline_formatting(line)}</p>')

        elif line == '':
            # Empty line - just skip
            pass

        i += 1

    # Add last section
    if current_section:
        html_sections.append({
            'id': current_section['id'],
            'title': current_section['title'],
            'level': current_section['level'],
            'content': '\n'.join(current_content)
        })

    return html_sections

def convert_table(rows):
    """Convert markdown table to HTML"""
    if len(rows) < 2:
        return ''

    html = '<table>\n'

    # Header row
    headers = [cell.strip() for cell in rows[0].split('|')[1:-1]]
    html += '<thead>\n<tr>\n'
    for header in headers:
        html += f'<th>{process_inline_formatting(header)}</th>\n'
    html += '</tr>\n</thead>\n'

    # Data rows (skip separator row)
    html += '<tbody>\n'
    for row in rows[2:]:
        cells = [cell.strip() for cell in row.split('|')[1:-1]]
        html += '<tr>\n'
        for cell in cells:
            html += f'<td>{process_inline_formatting(cell)}</td>\n'
        html += '</tr>\n'
    html += '</tbody>\n'
    html += '</table>\n'

    return html

def generate_full_html(md_file, output_file):
    """Generate complete HTML file"""
    sections = convert_markdown_to_html(md_file)

    # Read the current HTML template
    with open('/home/user/LPT/article.html', 'r', encoding='utf-8') as f:
        template = f.read()

    # Generate sections HTML
    sections_html = ''
    for section in sections:
        if section['level'] == 1:
            sections_html += f'''
<section id="{section['id']}" class="section">
    <h2>{process_inline_formatting(section['title'])}</h2>
    {section['content']}
</section>
'''
        elif section['level'] == 2:
            # Sub-sections are embedded in content
            sections_html += f'''
<section id="{section['id']}" class="section">
    <h2>{process_inline_formatting(section['title'])}</h2>
    {section['content']}
</section>
'''

    # Replace the article content in template
    # Find the main tag and replace its content
    import re
    pattern = r'(<main class="article">)(.*?)(</main>)'

    new_content = f'''\\1
            <header class="article-header">
                <h1>LPT — Liberté, Pression, Turbulence</h1>
                <p class="subtitle">Une théorie d'état empirique des sociétés modernes</p>
                <p class="author">Djamchid Dalili</p>
            </header>

{sections_html}

            <button id="backToTop" onclick="scrollToTop()">↑</button>
        \\3'''

    new_html = re.sub(pattern, new_content, template, flags=re.DOTALL)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"HTML file generated: {output_file}")

if __name__ == '__main__':
    generate_full_html('/home/user/LPT/LPT_article_V-dem (4).md', '/home/user/LPT/article_complete.html')
