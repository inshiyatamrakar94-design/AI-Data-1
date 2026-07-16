from fpdf import FPDF
import datetime
import os

def clean_pdf_text(text):
    """Replaces fancy unicode characters and emojis to prevent PDF crashes."""
    if not text:
        return ""
    replacements = {
        "💡": "Insight: ", "✨": "* ", "❓": "Q: ", "🧠": "Analysis: ",
        "—": "-", "–": "-", "•": "*", "“": '"', "”": '"', "‘": "'", "’": "'"
    }
    for bad_char, good_char in replacements.items():
        text = text.replace(bad_char, good_char)
    return text.encode('latin-1', 'ignore').decode('latin-1')

class ExecutiveReport(FPDF):
    def __init__(self, season_theme="Spring"):
        super().__init__()
        themes = {
            "Spring": {"primary": (46, 125, 50), "bg": (240, 249, 244), "text": (27, 94, 32)},
            "Summer": {"primary": (26, 54, 93), "bg": (240, 244, 250), "text": (44, 82, 130)},
            "Autumn": {"primary": (156, 66, 33), "bg": (255, 249, 242), "text": (92, 37, 18)},
            "Winter": {"primary": (30, 41, 59), "bg": (243, 244, 246), "text": (15, 23, 42)}
        }
        self.theme = themes.get(season_theme, themes["Spring"])

    def header(self):
        self.set_fill_color(*self.theme["primary"])
        self.rect(0, 0, 210, 15, "F")
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(255, 255, 255)
        self.set_y(3)
        self.cell(0, 10, "COMPREHENSIVE EXECUTIVE DATA SYSTEM REPORT", align="R")
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        self.cell(0, 10, f"Generated: {timestamp}", align="L")
        self.cell(0, 10, f"Page {self.page_no()}", align="R")

def compile_executive_pdf(username, industry, data_metrics, analysis_summary, faq_content, dataframe_sample=None, chart_paths=[], season_theme="Spring"):
    """Robust PDF compiler that dynamically handles incoming arguments safely."""
    pdf = ExecutiveReport(season_theme)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # 🎨 1. BANNER BLOCK
    pdf.set_y(22)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*pdf.theme["primary"])
    pdf.cell(0, 12, "Narrate a DATA : AI Storyteller Report", ln=True)
    pdf.ln(5)
    
    # 📊 2. METRICS PROFILE
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*pdf.theme["primary"])
    pdf.cell(0, 10, "1. Ingested Dataset Summary Profile", ln=True)
    
    # Type check to handle dictionary profiles safely
    if isinstance(data_metrics, dict):
        for key, value in data_metrics.items():
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(45, 6, f" {key}:", ln=False)
            pdf.set_font("Helvetica", "")
            pdf.cell(0, 6, f" {value}", ln=True)
    pdf.ln(6)
    
    # 📋 3. DATA SAMPLER TABLE GRID
    if dataframe_sample is not None and hasattr(dataframe_sample, 'columns'):
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*pdf.theme["primary"])
        pdf.cell(0, 10, "2. Extracted Dataset Grid Matrix (Sample Overview)", ln=True)
        pdf.ln(2)
        
        col_width = 190 / len(dataframe_sample.columns)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(*pdf.theme["primary"])
        pdf.set_text_color(255, 255, 255)
        for col in dataframe_sample.columns:
            pdf.cell(col_width, 7, clean_pdf_text(str(col))[:15], border=1, align="C", fill=True)
        pdf.ln()
        
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(40, 40, 40)
        for _, row in dataframe_sample.iterrows():
            for val in row:
                pdf.cell(col_width, 6, clean_pdf_text(str(val))[:15], border=1, align="L")
            pdf.ln()
        pdf.ln(8)

    # 📉 4. GRAPHIC VISUALS & CHARTS
    # 🔑 THE CRITICAL FIX: Explicitly ensure chart_paths is checked as a valid array loop
    if isinstance(chart_paths, list):
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*pdf.theme["primary"])
        pdf.cell(0, 10, "3. High-End Visualisation & Narrative Suite", ln=True)
        pdf.ln(2)
        
        for chart_info in chart_paths:
            if isinstance(chart_info, tuple) and len(chart_info) == 3:
                path, chart_title, narrative_text = chart_info
                if os.path.exists(str(path)):
                    if pdf.get_y() > 180: pdf.add_page()
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.cell(0, 6, f"Figure: {chart_title}", ln=True)
                    pdf.image(str(path), x=15, w=180, h=75)
                    pdf.ln(4)
                    pdf.set_font("Helvetica", "I", 9)
                    pdf.multi_cell(0, 5, f"AI System Context Analysis:\n{clean_pdf_text(narrative_text)}")
                    pdf.ln(8)

    # 📝 5. OVERALL STRATEGIC SUMMARY
    if pdf.get_y() > 200: pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*pdf.theme["primary"])
    pdf.cell(0, 10, "4. Overall Strategic Data Analysis Summary", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, clean_pdf_text(str(analysis_summary)))
    pdf.ln(6)
    
    # 🧠 6. DATA FAQ MATRIX
    if faq_content:
        if pdf.get_y() > 200: pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*pdf.theme["primary"])
        pdf.cell(0, 10, "5. Contextual Dataset FAQ Matrix", ln=True)
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, clean_pdf_text(str(faq_content)))
        
    return pdf.output(dest='S')
