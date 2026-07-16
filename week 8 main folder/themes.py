import streamlit as st

def apply_seasonal_theme(season_name):
    """Generates and injects highly vibrant custom visual styles for the platform."""
    
    # Upgraded palette structure featuring rich high-contrast corporate colors
    themes = {
        "Spring": {
            "background": "#F0F9F4",  # Fresh mint glow
            "sidebar": "#D1EAD8",     # Deep sage panel
            "accent": "#2E7D32",      # Emerald green highlights
            "text": "#1B5E20"         # Deep forest font
        },
        "Summer": {
            "background": "#F0F4FA",  # Bright morning sky blue tint
            "sidebar": "#BEE3F8",     # Rich turquoise coast panel
            "accent": "#1A365D",      # Deep executive navy buttons
            "text": "#2C5282"         # Crisp ocean blue labels
        },
        "Autumn": {
            "background": "#FFF9F2",  # Warm toasted pumpkin parchment
            "sidebar": "#FEEBC8",     # Rich golden honey panel
            "accent": "#9C4221",      # Deep rust crimson accents
            "text": "#5C2512"         # Dark roasted clove typography
        },
        "Winter": {
            "background": "#F3F4F6",  # Clear crisp glacier white
            "sidebar": "#CBD5E1",     # Solid metallic silver slate panel
            "accent": "#1E293B",      # Deep charcoal obsidian buttons
            "text": "#0F172A"         # Jet-black text for sharp contrast
        }
    }
    
    selected = themes.get(season_name, themes["Spring"])
    
    # Injecting advanced visual modifications directly into the rendering framework
    st.markdown(f"""
        <style>
        /* Base page background configuration */
        .stApp {{
            background-color: {selected['background']} !important;
            color: {selected['text']} !important;
        }}
        
        /* Left control panel container formatting and depth drop shadows */
        [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"] {{
            background-color: {selected['sidebar']} !important;
            border-right: 3px solid {selected['accent']};
            box-shadow: 4px 0px 10px rgba(0,0,0,0.05);
        }}
        
        /* High-contrast functional action button containers */
        .stButton>button {{
            background-color: {selected['accent']} !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
            border: 2px solid rgba(255,255,255,0.2) !important;
            padding: 0.5rem 1rem !important;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.1) !important;
            transition: all 0.2s ease-in-out !important;
        }}
        
        /* Active hover styling reactions */
        .stButton>button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0px 6px 12px rgba(0,0,0,0.15) !important;
            opacity: 0.95 !important;
        }}
        
        /* Checkbox text label isolation formatting */
        .stCheckbox label {{
            color: {selected['text']} !important;
            font-weight: 600 !important;
        }}
        
        /* Global typography tracking configuration overrides */
        h1, h2, h3, h4, p, label {{
            color: {selected['text']} !important;
            font-weight: 700;
        }}
        
        /* Clean box container structures for tables and analytics cards */
        div[data-testid="stExpander"], div.stElementContainer div[data-testid="element-container"] {{
            border-radius: 8px;
        }}
        </style>
    """, unsafe_allow_html=True)
