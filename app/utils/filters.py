from markupsafe import Markup, escape

def nl2br(value):
    """Convierte saltos de línea (\n) en etiquetas HTML <br>"""
    if not value:
        return ''
    
    value = escape(value)
    result = value.replace('\n', Markup('<br>\n'))
    return Markup(result) 