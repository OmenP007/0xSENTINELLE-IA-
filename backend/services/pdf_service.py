"""
Service de génération de Rapports PDF officiels PLCC pour 0xSentinelle IA
Génère un dossier de signalement prêt à envoyer à la PLCC (Côte d'Ivoire)
"""
import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_plcc_report(
    target_input: str,
    input_type: str,  # 'url', 'phone', 'text', 'voice'
    risk_level: str,
    risk_score: int,
    scam_type: str,
    target_brand: str,
    explanation: str,
    recommendations: list,
    technical_details: dict = None
) -> bytes:
    """Génère un PDF structuré de rapport de cybercriminalité au format octets."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Couleurs de la charte 0xSentinelle
    DARK_BLUE = colors.HexColor("#0f172a")
    ACCENT_RED = colors.HexColor("#ef4444")
    ACCENT_GREEN = colors.HexColor("#22c55e")
    ACCENT_YELLOW = colors.HexColor("#f59e0b")
    LIGHT_BG = colors.HexColor("#f8fafc")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=DARK_BLUE,
        alignment=1,
        spaceAfter=15
    )

    h2_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=DARK_BLUE,
        spaceBefore=12,
        spaceAfter=6
    )

    normal_style = ParagraphStyle(
        "NormalText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#334155"),
        leading=14
    )

    bold_label = ParagraphStyle(
        "BoldLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=DARK_BLUE,
        leading=14
    )

    badge_color = ACCENT_RED if risk_score >= 70 else (ACCENT_YELLOW if risk_score >= 40 else ACCENT_GREEN)

    story = []

    # 1. En-tête du Rapport
    story.append(Paragraph("🛡️ 0xSENTINELLE IA — RAPPORT DE SIGNALEMENT CYBERCRIMINEL", title_style))
    story.append(Paragraph("<b>Destinataire recommandé :</b> PLCC (Plateforme de Lutte Contre la Cybercriminalité — Côte d'Ivoire)", normal_style))
    story.append(Paragraph(f"<b>Date de génération :</b> {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M:%S UTC')}", normal_style))
    story.append(Paragraph("<b>Référence unique :</b> SENT-PLCC-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S"), normal_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=DARK_BLUE, spaceAfter=15))

    # 2. Résumé de la Menace (Tableau)
    summary_data = [
        [Paragraph("<b>Élément Analysé</b>", bold_label), Paragraph(f"<code>{target_input}</code>", normal_style)],
        [Paragraph("<b>Type d'entrée</b>", bold_label), Paragraph(input_type.upper(), normal_style)],
        [Paragraph("<b>Niveau de Risque</b>", bold_label), Paragraph(f"<font color='{badge_color.hexval()}'><b>{risk_level} ({risk_score}/100)</b></font>", normal_style)],
        [Paragraph("<b>Type d'Escroquerie</b>", bold_label), Paragraph(scam_type, normal_style)],
        [Paragraph("<b>Marque Ciblée / Usurpée</b>", bold_label), Paragraph(target_brand or "Non spécifiée / Inconnue", normal_style)],
    ]

    t_summary = Table(summary_data, colWidths=[160, 350])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 15))

    # 3. Explication et Analyse de l'IA
    story.append(Paragraph("📌 Synthèse d'Analyse et Constats d'Ingénierie Sociale", h2_style))
    story.append(Paragraph(explanation, normal_style))
    story.append(Spacer(1, 12))

    # 4. Recommandations Conservatoires
    story.append(Paragraph("⚠️ Mesures Préventives Immédiates", h2_style))
    rec_html = "<br/>".join([f"• {r}" for r in recommendations]) if recommendations else "• Ne communiquez aucune donnée sensible."
    story.append(Paragraph(rec_html, normal_style))
    story.append(Spacer(1, 15))

    # 5. Contacts d'urgence PLCC Côte d'Ivoire
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=10, spaceAfter=10))
    story.append(Paragraph("📞 <b>Procédure de Dépôt Officiel de Plainte (PLCC Côte d'Ivoire)</b>", h2_style))
    contact_text = (
        "En cas de préjudice financier ou de vol de données personnelles, veuillez transmettre ce rapport aux autorités :<br/>"
        "• <b>Email direct PLCC :</b> cybercrime@interieur.gouv.ci<br/>"
        "• <b>Téléphone direct :</b> +225 27 22 48 94 00 / +225 07 07 48 94 00<br/>"
        "• <b>Locaux :</b> Abidjan Cocody II Plateaux, Direction de l'Informatique et des Traces Technologiques (DITT)"
    )
    story.append(Paragraph(contact_text, normal_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
