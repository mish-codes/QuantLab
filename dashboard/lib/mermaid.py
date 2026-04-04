"""Render Mermaid diagrams in Streamlit via components.html."""
import base64
import hashlib
import streamlit.components.v1 as components


def render_mermaid(diagram: str, height: int = 400) -> None:
    """Render a Mermaid diagram inside an HTML component.

    Base64-encodes the diagram to avoid escaping issues with
    special characters in Mermaid syntax (arrows, braces, etc).
    """
    uid = "m" + hashlib.md5(diagram.encode()).hexdigest()[:8]
    b64 = base64.b64encode(diagram.strip().encode()).decode()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 8px; background: white; font-family: sans-serif; }}
            #output-{uid} {{ min-height: 50px; }}
            .error {{ color: red; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div id="output-{uid}"></div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: false, theme: 'default', securityLevel: 'loose' }});
            const diagram = atob('{b64}');
            try {{
                const {{ svg }} = await mermaid.render('{uid}', diagram);
                document.getElementById('output-{uid}').innerHTML = svg;
            }} catch(e) {{
                document.getElementById('output-{uid}').innerHTML = '<p class="error">' + e.message + '</p>';
            }}
        </script>
    </body>
    </html>
    """
    components.html(html, height=height)
