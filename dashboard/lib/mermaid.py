"""Render Mermaid diagrams in Streamlit via components.html."""
import streamlit.components.v1 as components


def render_mermaid(diagram: str, height: int = 400) -> None:
    """Render a Mermaid diagram inside an HTML component.

    The raw diagram text is hidden. Only the rendered SVG is shown.
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 8px; background: white; font-family: sans-serif; }}
            #raw {{ display: none; }}
            #output {{ min-height: 50px; }}
        </style>
    </head>
    <body>
        <div id="raw">{diagram}</div>
        <div id="output"></div>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{ startOnLoad: false, theme: 'default', securityLevel: 'loose' }});
            mermaid.render('mermaid-svg', document.getElementById('raw').textContent).then(function(result) {{
                document.getElementById('output').innerHTML = result.svg;
            }}).catch(function(err) {{
                document.getElementById('output').innerHTML = '<p style="color:red;">Diagram render error: ' + err + '</p>';
            }});
        </script>
    </body>
    </html>
    """
    components.html(html, height=height)
