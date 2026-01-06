#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple and faithful markdown to HTML converter for LPT article
Preserves all text exactly - only adds HTML tags
"""

import re
import html

# Read markdown
with open('/home/user/LPT/LPT_article_V-dem (4).md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# Image mappings
IMAGES = {
    '[image1]': 'Figure1_Global_PL.png',
    '[image2]': 'Figure1bis_Global_LY.png',
    '[image3]': 'Figure2_Trajectoires_LP.png',
    '[image4]': 'Figure2bis_Trajectoires_LY.png',
    '[image5]': 'Figure3_Bootstrap_b.png',
    '[image6]': 'Figure_C1_L_vs_P.png',
    '[image7]': 'Figure_C1bis_Y_vs_L.png',
    '[image8]': 'Figure_C2_Trajectories_LP.png',
    '[image9]': 'Figure_C2bis_Trajectories_LY.png',
    '[image10]': 'Figure_D1_AI_Scaled.png',
}

def inline_format(text):
    """Apply inline formatting (bold, italic) - preserves text content"""
    # Bold **text**
    text = re.sub(r'\*\*([^\*]+?)\*\*', r'<strong>\1</strong>', text)
    # Italic *text* (not part of **)
    text = re.sub(r'(?<![*])(\*)(?!\*)([^*]+?)(?<![*])\1(?![*])', r'<em>\2</em>', text)
    return text

def process_line(line):
    """Process a single line - NO text modification, only HTML tagging"""
    line = line.rstrip('\n')

    # Empty line
    if not line.strip():
        return ''

    # Headers
    if line.startswith('# '):
        text = line[2:].strip().strip('*').strip()
        return f'<h1>{inline_format(text)}</h1>\n'
    elif line.startswith('## '):
        text = line[3:].strip().strip('*').strip()
        return f'<h2>{inline_format(text)}</h2>\n'
    elif line.startswith('### '):
        text = line[4:].strip().strip('*').strip()
        return f'<h3>{inline_format(text)}</h3>\n'
    elif line.startswith('#### '):
        text = line[5:].strip().strip('*').strip()
        return f'<h4>{inline_format(text)}</h4>\n'

    # Horizontal rule
    if line.strip() == '---':
        return '<hr>\n'

    # Image references
    if '**![][image' in line or '*![][image' in line:
        for img_ref, img_file in IMAGES.items():
            if img_ref in line:
                fig_num = img_ref.replace('[image', '').replace(']', '')
                return f'<div class="figure-placeholder" data-image="{img_file}" data-fignum="{fig_num}"></div>\n'

    # Table rows
    if line.startswith('|'):
        return line + '\n'

    # Regular paragraph
    return f'<p>{inline_format(line)}</p>\n'

# Process markdown line by line
lines = md_content.split('\n')
html_body = []
in_table = False
table_lines = []

for i, line in enumerate(lines):
    # Table handling
    if line.startswith('|'):
        if not in_table:
            in_table = True
            table_lines = []
        table_lines.append(line)
    else:
        # End of table
        if in_table:
            # Convert table
            html_body.append('<table>')
            if len(table_lines) > 0:
                # Header
                headers = [c.strip() for c in table_lines[0].split('|')[1:-1]]
                html_body.append('<thead><tr>')
                for h in headers:
                    html_body.append(f'<th>{inline_format(h)}</th>')
                html_body.append('</tr></thead>')

                # Rows (skip separator line)
                if len(table_lines) > 2:
                    html_body.append('<tbody>')
                    for row_line in table_lines[2:]:
                        cells = [c.strip() for c in row_line.split('|')[1:-1]]
                        html_body.append('<tr>')
                        for cell in cells:
                            html_body.append(f'<td>{inline_format(cell)}</td>')
                        html_body.append('</tr>')
                    html_body.append('</tbody>')
            html_body.append('</table>')
            in_table = False
            table_lines = []

        # Process non-table line
        if line.strip():
            html_body.append(process_line(line))

# Create final HTML
html_output = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LPT — Liberté, Pression, Turbulence</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <aside class="toc" id="toc">
            <h3>Table des matières</h3>
            <nav id="toc-nav"></nav>
        </aside>

        <main class="article">
            <header class="article-header">
                <h1>LPT — Liberté, Pression, Turbulence</h1>
                <p class="subtitle">Une théorie d'état empirique des sociétés modernes</p>
                <p class="author">Djamchid Dalili</p>
            </header>

            <div class="article-content">
                {''.join(html_body)}
            </div>

            <button id="backToTop" onclick="scrollToTop()">↑</button>
        </main>
    </div>

    <div id="imageModal" class="modal" onclick="closeModal()">
        <span class="close">&times;</span>
        <img class="modal-content" id="modalImg">
        <div id="caption"></div>
    </div>

    <script src="script.js"></script>
    <script>
        // Replace figure placeholders with actual figures
        document.addEventListener('DOMContentLoaded', function() {{
            const placeholders = document.querySelectorAll('.figure-placeholder');
            placeholders.forEach(placeholder => {{
                const imgFile = placeholder.getAttribute('data-image');
                const figNum = placeholder.getAttribute('data-fignum');
                const figure = document.createElement('figure');
                figure.className = 'figure';
                figure.id = 'figure' + figNum;

                const img = document.createElement('img');
                img.src = imgFile;
                img.alt = 'Figure ' + figNum;
                img.onclick = function() {{ zoomImage(this); }};

                figure.appendChild(img);

                // Check if next element is a paragraph for caption
                const nextEl = placeholder.nextElementSibling;
                if (nextEl && nextEl.tagName === 'P' && nextEl.textContent.includes('Figure')) {{
                    const figcaption = document.createElement('figcaption');
                    figcaption.innerHTML = nextEl.innerHTML;
                    figure.appendChild(figcaption);
                    nextEl.remove();
                }}

                placeholder.replaceWith(figure);
            }});
        }});
    </script>
</body>
</html>
'''

# Write output
with open('/home/user/LPT/article_full.html', 'w', encoding='utf-8') as f:
    f.write(html_output)

print("✓ HTML file generated: article_full.html")
print(f"✓ Processed {len(lines)} lines")
print(f"✓ Found {len([l for l in html_body if '<table>' in l])} tables")
