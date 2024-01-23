def remove_srid(wkt_with_srid):
    """
    Remove the SRID from a WKT string if it exists.
    
    Args:
        wkt_with_srid (str): The WKT string with possible SRID prefix.
    
    Returns:
        str: The WKT string without the SRID prefix.
    """
    if wkt_with_srid.upper().startswith('SRID'):
        first_semicolon_index = wkt_with_srid.find(';')
        if first_semicolon_index != -1:
            wkt = wkt_with_srid[first_semicolon_index+1:]
            return wkt
    return wkt_with_srid

def extract_srid(wkt_text):
    if wkt_text.upper().startswith('SRID'):
        srid, wkt = wkt_text.split(';', 1)
        srid = srid.split('=')[1]
        return srid, wkt
    return None, wkt_text

def generate_wkt_with_srid(srid, wkt_text):
    if srid is not None:
        return f"SRID={srid};" + wkt_text
    return wkt_text