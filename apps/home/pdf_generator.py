# ============================================================
# JADWAPLAN PROFESSIONAL PDF GENERATOR - v4
# ============================================================
#
# FEATURES:
# - Tables and titles kept together (no page breaks in middle)
# - Subsection headers always have content with them
# - Appendix shows actual images embedded
# - PDFs shown as styled info boxes (no Poppler required)
#
# SETUP:
# 1. Copy jadwaplan_logo.png to apps/static/assets/img/
# 2. pip install reportlab matplotlib pillow
#
# ============================================================

import io
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable, KeepTogether, CondPageBreak
)

# For matplotlib charts
try:
    import matplotlib

    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# For image handling
try:
    from PIL import Image as PILImage

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# For PDF rendering (PyMuPDF - no Poppler needed!)
try:
    import fitz  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class JadwaColors:
    BLUE = colors.HexColor('#4F7DF3')
    CHARCOAL = colors.HexColor('#1A1A24')
    GRAY_DARK = colors.HexColor('#4A4A5A')
    GRAY = colors.HexColor('#6B6B7A')
    GRAY_LIGHT = colors.HexColor('#9A9AAA')
    GRAY_PALE = colors.HexColor('#E5E5EA')
    WHITE = colors.HexColor('#FFFFFF')
    OFF_WHITE = colors.HexColor('#F8F9FC')
    SUCCESS = colors.HexColor('#10B981')
    WARNING = colors.HexColor('#F59E0B')
    INFO = colors.HexColor('#06B6D4')
    RED_LIGHT = colors.HexColor('#FEE2E2')
    RED = colors.HexColor('#DC2626')


def get_jadwa_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='JadwaH1', parent=styles['Heading1'], fontSize=22,
                              textColor=JadwaColors.CHARCOAL, spaceBefore=30, spaceAfter=15, fontName='Helvetica-Bold',
                              keepWithNext=True))

    styles.add(ParagraphStyle(name='JadwaH2', parent=styles['Heading2'], fontSize=14,
                              textColor=JadwaColors.BLUE, spaceBefore=20, spaceAfter=10, fontName='Helvetica-Bold',
                              keepWithNext=True))

    styles.add(ParagraphStyle(name='JadwaBody', parent=styles['Normal'], fontSize=11,
                              textColor=JadwaColors.GRAY_DARK, alignment=TA_JUSTIFY, spaceBefore=6, spaceAfter=10,
                              leading=16))

    styles.add(ParagraphStyle(name='JadwaMVOTitle', parent=styles['Normal'], fontSize=10,
                              textColor=JadwaColors.BLUE, fontName='Helvetica-Bold', spaceAfter=5))

    styles.add(ParagraphStyle(name='JadwaMVOContent', parent=styles['Normal'], fontSize=10,
                              textColor=JadwaColors.GRAY_DARK, leading=14))

    styles.add(ParagraphStyle(name='JadwaChartTitle', parent=styles['Normal'], fontSize=12,
                              textColor=JadwaColors.CHARCOAL, fontName='Helvetica-Bold', alignment=TA_CENTER,
                              spaceBefore=10, spaceAfter=10, keepWithNext=True))

    styles.add(ParagraphStyle(name='JadwaDocItem', parent=styles['Normal'], fontSize=10,
                              textColor=JadwaColors.GRAY_DARK, leading=14))

    styles.add(ParagraphStyle(name='JadwaDocTitle', parent=styles['Normal'], fontSize=12,
                              textColor=JadwaColors.CHARCOAL, fontName='Helvetica-Bold', spaceBefore=15, spaceAfter=8,
                              alignment=TA_CENTER))

    styles.add(ParagraphStyle(name='JadwaDocDesc', parent=styles['Normal'], fontSize=10,
                              textColor=JadwaColors.GRAY, alignment=TA_CENTER, spaceAfter=10))

    styles.add(ParagraphStyle(name='JadwaDocType', parent=styles['Normal'], fontSize=9,
                              textColor=JadwaColors.GRAY_LIGHT, alignment=TA_CENTER, spaceBefore=5))

    return styles


class JadwaPlanPDF:

    def __init__(self, filename, lang='en', logo_path=None):
        self.filename = filename
        self.lang = lang
        self.styles = get_jadwa_styles()
        self.story = []
        self.page_width, self.page_height = A4

        self.logo_path = logo_path
        if not self.logo_path:
            for path in ['apps/static/assets/img/jadwaplan_logo.png',
                         'apps/static/assets/img/Jadwa_plan_logo_final_version_-_transp-01.png']:
                if os.path.exists(path):
                    self.logo_path = path
                    break

        self.left_margin = self.right_margin = self.top_margin = self.bottom_margin = 1 * inch
        self.content_width = self.page_width - self.left_margin - self.right_margin
        self.content_height = self.page_height - self.top_margin - self.bottom_margin
        self.business_name = ""
        self.generated_date = datetime.now().strftime("%B %d, %Y")

    def _t(self, en, ar):
        return ar if self.lang == 'ar' else en

    def add_cover_page(self, business_name):
        self.business_name = business_name
        self.story.append(Spacer(1, 1.5 * inch))

        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo = Image(self.logo_path, width=3.5 * inch, height=1 * inch)
                logo.hAlign = 'CENTER'
                self.story.append(logo)
            except:
                self._add_text_logo()
        else:
            self._add_text_logo()

        self.story.append(Spacer(1, 1.5 * inch))
        self.story.append(HRFlowable(width="60%", thickness=3, color=JadwaColors.BLUE, spaceBefore=20, spaceAfter=20,
                                     hAlign='CENTER'))
        self.story.append(Spacer(1, 0.5 * inch))

        self.story.append(Paragraph(self._t("Business Plan", "خطة العمل"),
                                    ParagraphStyle(name='CT', fontSize=28, textColor=JadwaColors.CHARCOAL,
                                                   alignment=TA_CENTER, fontName='Helvetica-Bold')))
        self.story.append(Spacer(1, 20))
        self.story.append(Paragraph(business_name,
                                    ParagraphStyle(name='BN', fontSize=24, textColor=JadwaColors.BLUE,
                                                   alignment=TA_CENTER, fontName='Helvetica-Bold')))
        self.story.append(Spacer(1, 2.5 * inch))
        self.story.append(Paragraph(f"{self._t('Generated on', 'تم الإنشاء في')}: {self.generated_date}",
                                    ParagraphStyle(name='D', fontSize=11, textColor=JadwaColors.GRAY,
                                                   alignment=TA_CENTER)))
        self.story.append(PageBreak())

    def _add_text_logo(self):
        self.story.append(Paragraph('<font color="#1A1A24">JADWA</font><font color="#4F7DF3">PLAN</font>',
                                    ParagraphStyle(name='L', fontSize=36, alignment=TA_CENTER,
                                                   fontName='Helvetica-Bold')))
        self.story.append(Spacer(1, 10))
        self.story.append(Paragraph("we make small businesses finance-ready",
                                    ParagraphStyle(name='T', fontSize=11, textColor=JadwaColors.GRAY,
                                                   alignment=TA_CENTER)))

    def add_table_of_contents(self, sections):
        self.story.append(Paragraph(self._t("Table of Contents", "جدول المحتويات"), self.styles['JadwaH1']))
        self.story.append(Spacer(1, 20))
        for i, section in enumerate(sections, 1):
            self.story.append(Paragraph(f"{i}. {section}",
                                        ParagraphStyle(name='TOC', fontSize=12, textColor=JadwaColors.GRAY_DARK,
                                                       leading=24)))
        self.story.append(PageBreak())

    def add_mvo_section(self, mission="", vision="", objectives=""):
        if not any([mission, vision, objectives]):
            return
        self.story.append(
            Paragraph(self._t("Mission, Vision & Objectives", "المهمة والرؤية والأهداف"), self.styles['JadwaH1']))

        for title, content, color in [(self._t("MISSION", "المهمة"), mission, JadwaColors.BLUE),
                                      (self._t("VISION", "الرؤية"), vision, JadwaColors.SUCCESS),
                                      (self._t("OBJECTIVES", "الأهداف"), objectives, JadwaColors.WARNING)]:
            if content:
                box = Table(
                    [[Paragraph(f'<font color="{color.hexval()}">{title}</font>', self.styles['JadwaMVOTitle'])],
                     [Paragraph(content, self.styles['JadwaMVOContent'])]], colWidths=[self.content_width - 20])
                box.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), JadwaColors.OFF_WHITE),
                                         ('BOX', (0, 0), (-1, -1), 1, JadwaColors.GRAY_PALE),
                                         ('PADDING', (0, 0), (-1, -1), 15)]))
                self.story.append(KeepTogether([box, Spacer(1, 15)]))

    def add_section(self, title, new_page=False):
        if new_page:
            self.story.append(PageBreak())
        self.story.append(
            HRFlowable(width="100%", thickness=3, color=JadwaColors.BLUE, spaceBefore=10, spaceAfter=0, hAlign='LEFT'))
        self.story.append(Paragraph(title, self.styles['JadwaH1']))

    def add_subsection(self, title):
        self.story.append(CondPageBreak(1.5 * inch))
        self.story.append(Paragraph(title, self.styles['JadwaH2']))

    def add_text(self, text):
        if text:
            self.story.append(Paragraph(text, self.styles['JadwaBody']))

    def add_page_break(self):
        self.story.append(PageBreak())

    def add_table(self, headers, data, col_widths=None, keep_together=True):
        if not col_widths:
            col_widths = [self.content_width / len(headers)] * len(headers)
        table = Table([headers] + data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), JadwaColors.CHARCOAL), ('TEXTCOLOR', (0, 0), (-1, 0), JadwaColors.WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'), ('PADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [JadwaColors.WHITE, JadwaColors.OFF_WHITE]),
            ('GRID', (0, 0), (-1, -1), 0.5, JadwaColors.GRAY_PALE)]))

        if keep_together:
            self.story.append(KeepTogether([table, Spacer(1, 15)]))
        else:
            self.story.append(table)
            self.story.append(Spacer(1, 15))

    def add_summary_table(self, label, value, is_total=False):
        bg = JadwaColors.BLUE if is_total else JadwaColors.OFF_WHITE
        tc = JadwaColors.WHITE if is_total else JadwaColors.CHARCOAL
        table = Table([[label, value]], colWidths=[self.content_width * 0.7, self.content_width * 0.3])
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg), ('TEXTCOLOR', (0, 0), (-1, -1), tc),
                                   ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                                   ('ALIGN', (0, 0), (-1, -1), 'RIGHT'), ('PADDING', (0, 0), (-1, -1), 12)]))
        self.story.append(KeepTogether([table, Spacer(1, 10)]))

    def add_bar_chart(self, title, labels, datasets, width=450, height=250):
        elements = []
        elements.append(Paragraph(title, self.styles['JadwaChartTitle']))

        if MATPLOTLIB_AVAILABLE:
            fig, ax = plt.subplots(figsize=(width / 72, height / 72), dpi=72)
            x = range(len(labels))
            bar_width = 0.8 / len(datasets)
            colors_list = ['#4F7DF3', '#1A1A24', '#F59E0B', '#10B981', '#8B5CF6', '#EC4899']
            for i, ds in enumerate(datasets):
                offset = (i - len(datasets) / 2 + 0.5) * bar_width
                ax.bar([xi + offset for xi in x], ds['data'], bar_width, label=ds['label'],
                       color=colors_list[i % len(colors_list)])
            ax.set_xticks(x)
            ax.set_xticklabels(labels, fontsize=9)
            ax.legend(loc='upper right', fontsize=9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.yaxis.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            plt.close()
            elements.append(Image(buf, width=width, height=height))

        elements.append(Spacer(1, 10))

        headers = [self._t("Category", "الفئة")] + [d['label'] for d in datasets]
        data = [[label] + [f"{d['data'][i]:,.0f}" for d in datasets] for i, label in enumerate(labels)]
        col_widths = [self.content_width / len(headers)] * len(headers)
        table = Table([headers] + data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), JadwaColors.CHARCOAL), ('TEXTCOLOR', (0, 0), (-1, 0), JadwaColors.WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'), ('PADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [JadwaColors.WHITE, JadwaColors.OFF_WHITE]),
            ('GRID', (0, 0), (-1, -1), 0.5, JadwaColors.GRAY_PALE)]))
        elements.append(table)
        elements.append(Spacer(1, 15))

        self.story.append(KeepTogether(elements))

    def add_pie_chart(self, title, labels, data, width=350, height=250):
        elements = []
        elements.append(Paragraph(title, self.styles['JadwaChartTitle']))

        if MATPLOTLIB_AVAILABLE:
            fig, ax = plt.subplots(figsize=(width / 72, height / 72), dpi=72)
            colors_list = ['#4F7DF3', '#1A1A24', '#F59E0B', '#10B981', '#8B5CF6', '#EC4899', '#06B6D4']
            wedges, texts, autotexts = ax.pie(data, labels=labels, autopct='%1.1f%%',
                                              colors=colors_list[:len(data)], wedgeprops=dict(width=0.6),
                                              pctdistance=0.75)
            for at in autotexts:
                at.set_fontsize(9)
                at.set_color('white')
            for t in texts:
                t.set_fontsize(9)
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            plt.close()
            elements.append(Image(buf, width=width, height=height))

        elements.append(Spacer(1, 10))

        total = sum(data)
        headers = [self._t("Segment", "الشريحة"), self._t("Value", "القيمة"), self._t("Percentage", "النسبة")]
        tdata = [[l, f"{v:,.0f}", f"{(v / total * 100) if total else 0:.1f}%"] for l, v in zip(labels, data)]
        col_widths = [self.content_width * 0.5, self.content_width * 0.25, self.content_width * 0.25]
        table = Table([headers] + tdata, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), JadwaColors.CHARCOAL), ('TEXTCOLOR', (0, 0), (-1, 0), JadwaColors.WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'), ('PADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [JadwaColors.WHITE, JadwaColors.OFF_WHITE]),
            ('GRID', (0, 0), (-1, -1), 0.5, JadwaColors.GRAY_PALE)]))
        elements.append(table)
        elements.append(Spacer(1, 15))

        self.story.append(KeepTogether(elements))

    def add_radar_chart(self, title, categories, datasets, width=350, height=300):
        """Radar chart for supplier comparison"""
        elements = []
        elements.append(Paragraph(title, self.styles['JadwaChartTitle']))

        if MATPLOTLIB_AVAILABLE and datasets:
            import numpy as np
            fig, ax = plt.subplots(figsize=(width / 72, height / 72), subplot_kw=dict(polar=True), dpi=72)
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]

            colors_list = ['#4F7DF3', '#1A1A24', '#F59E0B', '#10B981']
            for i, ds in enumerate(datasets[:4]):
                values = ds['data'] + ds['data'][:1]
                ax.plot(angles, values, 'o-', linewidth=2, label=ds['label'], color=colors_list[i % 4], markersize=5)
                ax.fill(angles, values, alpha=0.15, color=colors_list[i % 4])

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=9)
            ax.set_ylim(0, 5)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=8)
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            plt.close()
            elements.append(Image(buf, width=width, height=height))

        elements.append(Spacer(1, 15))
        self.story.append(KeepTogether(elements))

    def add_gauge_chart(self, title, current, maximum, width=300, height=200):
        """Semi-circular gauge for capacity utilization"""
        elements = []
        elements.append(Paragraph(title, self.styles['JadwaChartTitle']))

        if MATPLOTLIB_AVAILABLE and maximum > 0:
            import numpy as np
            fig, ax = plt.subplots(figsize=(width / 72, height / 72), dpi=72)
            percentage = (current / maximum) * 100

            # Color based on utilization
            if percentage > 90:
                gauge_color = '#EF4444'
            elif percentage > 75:
                gauge_color = '#F59E0B'
            else:
                gauge_color = '#10B981'

            # Draw gauge
            theta = np.linspace(0, np.pi, 100)
            ax.fill_between(np.cos(theta), np.sin(theta), 0, color='#E5E5EA', alpha=0.5)

            filled_angle = np.pi * (percentage / 100)
            theta_filled = np.linspace(0, filled_angle, 100)
            ax.fill_between(np.cos(theta_filled), np.sin(theta_filled), 0, color=gauge_color, alpha=0.8)

            # Center circle
            circle = plt.Circle((0, 0), 0.6, color='white', zorder=10)
            ax.add_patch(circle)

            # Text
            ax.text(0, 0.1, f'{percentage:.1f}%', ha='center', va='center', fontsize=18, fontweight='bold', zorder=11)
            ax.text(0, -0.15, 'Utilization', ha='center', va='center', fontsize=9, color='#6B6B7A', zorder=11)

            ax.set_xlim(-1.2, 1.2)
            ax.set_ylim(-0.3, 1.2)
            ax.set_aspect('equal')
            ax.axis('off')
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            plt.close()
            elements.append(Image(buf, width=width, height=height))

        elements.append(Spacer(1, 15))
        self.story.append(KeepTogether(elements))

    def add_horizontal_bar_chart(self, title, labels, values, width=400, height=200):
        """Horizontal bar chart for experience timeline"""
        elements = []
        elements.append(Paragraph(title, self.styles['JadwaChartTitle']))

        if MATPLOTLIB_AVAILABLE and labels and values:
            import numpy as np
            fig_height = max(2, len(labels) * 0.5)
            fig, ax = plt.subplots(figsize=(width / 72, fig_height), dpi=72)

            colors_list = ['#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#4F7DF3', '#06B6D4']
            y_pos = np.arange(len(labels))
            bars = ax.barh(y_pos, values, color=[colors_list[i % 6] for i in range(len(labels))], height=0.6)

            ax.set_yticks(y_pos)
            ax.set_yticklabels(labels, fontsize=9)
            ax.invert_yaxis()

            for bar, val in zip(bars, values):
                ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2, f'{val} yrs', va='center',
                        fontsize=9)

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.xaxis.set_visible(False)
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            plt.close()

            chart_height = max(150, len(labels) * 35)
            elements.append(Image(buf, width=width, height=chart_height))

        elements.append(Spacer(1, 15))
        self.story.append(KeepTogether(elements))

    def add_ownership_chart(self, title, owner_data, width=350, height=250):
        """Ownership donut chart with owner highlighted"""
        elements = []
        elements.append(Paragraph(title, self.styles['JadwaChartTitle']))

        if MATPLOTLIB_AVAILABLE and owner_data:
            fig, ax = plt.subplots(figsize=(width / 72, height / 72), dpi=72)

            labels = [d['name'] for d in owner_data]
            sizes = [d['shares'] for d in owner_data]
            colors_list = ['#4F7DF3'] + ['#1A1A24', '#F59E0B', '#10B981', '#8B5CF6', '#EC4899'][:len(owner_data) - 1]
            explode = [0.05] + [0] * (len(owner_data) - 1)  # Highlight first (owner)

            wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.0f%%', colors=colors_list,
                                              explode=explode,
                                              wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2),
                                              pctdistance=0.75)
            for at in autotexts:
                at.set_fontsize(9)
                at.set_fontweight('bold')

            ax.text(0, 0.05, '100%', ha='center', va='center', fontsize=16, fontweight='bold')
            ax.text(0, -0.12, 'Ownership', ha='center', va='center', fontsize=9, color='#6B6B7A')
            ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=9)
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            plt.close()
            elements.append(Image(buf, width=width, height=height))

        # Add table
        elements.append(Spacer(1, 10))
        headers = [self._t("Owner/Partner", "المالك/الشريك"), self._t("Shares %", "نسبة الملكية")]
        tdata = [[d['name'], f"{d['shares']}%"] for d in owner_data]
        table = Table([headers] + tdata, colWidths=[self.content_width * 0.5, self.content_width * 0.25])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), JadwaColors.CHARCOAL),
            ('TEXTCOLOR', (0, 0), (-1, 0), JadwaColors.WHITE),
            ('BACKGROUND', (0, 1), (-1, 1), JadwaColors.BLUE),  # Highlight owner row
            ('TEXTCOLOR', (0, 1), (-1, 1), JadwaColors.WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, JadwaColors.GRAY_PALE)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 15))

        self.story.append(KeepTogether(elements))


    def add_projections_table(self, projections, total_projections, inflation_rate):
        self.add_subsection(self._t(f"Financial Projections (5 Years) - Inflation: {inflation_rate}%",
                                    f"التوقعات المالية (5 سنوات) - التضخم: {inflation_rate}%"))

        headers = [self._t("Item", "البند")] + [self._t(f"Year {i}", f"السنة {i}") for i in range(1, 6)]
        data = []

        for item in projections:
            if item.get('type') == 'product':
                row = [f"{item.get('name', '')} - Revenue"]
                for year in item.get('years', []):
                    row.append(f"${year.get('revenue', 0):,.0f}")
                data.append(row)

        rev_row = [self._t("TOTAL REVENUE", "إجمالي الإيرادات")]
        for year in total_projections.get('years', []):
            rev_row.append(f"${year.get('grand_total_revenue', 0):,.0f}")
        data.append(rev_row)

        for item in projections:
            if item.get('type') == 'expense' and item.get('name') != 'Total Operating Expenses':
                row = [item.get('name', '')]
                for year in item.get('years', []):
                    row.append(f"${year.get('amount', 0):,.0f}")
                data.append(row)

        exp_row = [self._t("TOTAL EXPENSES", "إجمالي المصاريف")]
        for year in total_projections.get('years', []):
            exp_row.append(f"${year.get('total_operating_expenses', 0):,.0f}")
        data.append(exp_row)

        prof_row = [self._t("NET PROFIT", "صافي الربح")]
        for year in total_projections.get('years', []):
            prof_row.append(f"${year.get('profit', 0):,.0f}")
        data.append(prof_row)

        marg_row = [self._t("PROFIT MARGIN", "هامش الربح")]
        for year in total_projections.get('years', []):
            marg_row.append(f"{year.get('margin', 0):.1f}%")
        data.append(marg_row)

        col_widths = [self.content_width * 0.3] + [self.content_width * 0.14] * 5
        table = Table([headers] + data, colWidths=col_widths, repeatRows=1)
        style_cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), JadwaColors.CHARCOAL), ('TEXTCOLOR', (0, 0), (-1, 0), JadwaColors.WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'), ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, JadwaColors.GRAY_PALE)]
        for i, row in enumerate(data, 1):
            if 'TOTAL' in row[0] or 'NET' in row[0] or 'MARGIN' in row[0]:
                style_cmds.append(('BACKGROUND', (0, i), (-1, i), JadwaColors.OFF_WHITE))
                style_cmds.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
            if 'NET PROFIT' in row[0] or 'صافي' in row[0]:
                style_cmds.append(('BACKGROUND', (0, i), (-1, i), JadwaColors.BLUE))
                style_cmds.append(('TEXTCOLOR', (0, i), (-1, i), JadwaColors.WHITE))
        table.setStyle(TableStyle(style_cmds))
        self.story.append(table)
        self.story.append(Spacer(1, 20))

    def add_image_gallery(self, image_paths, images_per_row=2):
        if not image_paths:
            return
        img_width = (self.content_width - 20) / images_per_row
        rows, current_row = [], []
        for path in image_paths:
            if os.path.exists(path):
                try:
                    img = Image(path, width=img_width - 10, height=(img_width - 10) * 0.75)
                    current_row.append(img)
                    if len(current_row) >= images_per_row:
                        rows.append(current_row)
                        current_row = []
                except Exception as e:
                    print(f"Error loading {path}: {e}")
        if current_row:
            while len(current_row) < images_per_row:
                current_row.append('')
            rows.append(current_row)
        if rows:
            table = Table(rows, colWidths=[img_width] * images_per_row)
            table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                       ('PADDING', (0, 0), (-1, -1), 5)]))
            self.story.append(table)
            self.story.append(Spacer(1, 15))

    def _get_file_size_str(self, filepath):
        """Get human-readable file size"""
        try:
            size = os.path.getsize(filepath)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except:
            return "Unknown size"

    def _embed_document(self, doc_path, filename, description="", doc_number=1):
        """Embed a document - images shown directly, PDFs rendered as images"""
        elements = []

        ext = os.path.splitext(filename)[1].lower()
        max_img_width = self.content_width * 0.95
        max_img_height = self.content_height * 0.75

        # Document header
        elements.append(Paragraph(f"Document {doc_number}: {filename}", self.styles['JadwaDocTitle']))
        if description:
            elements.append(Paragraph(description, self.styles['JadwaDocDesc']))

        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
            # It's an image - embed directly
            try:
                if PIL_AVAILABLE:
                    pil_img = PILImage.open(doc_path)
                    img_width, img_height = pil_img.size
                    aspect = img_width / img_height

                    display_width = min(img_width, max_img_width)
                    display_height = display_width / aspect
                    if display_height > max_img_height:
                        display_height = max_img_height
                        display_width = display_height * aspect

                    pil_img.close()
                else:
                    display_width = max_img_width * 0.8
                    display_height = max_img_height * 0.6

                img = Image(doc_path, width=display_width, height=display_height)
                img.hAlign = 'CENTER'
                elements.append(Spacer(1, 10))
                elements.append(img)

            except Exception as e:
                print(f"Error embedding image {filename}: {e}")
                elements.append(Paragraph(f"[Could not load image: {filename}]", self.styles['JadwaDocDesc']))

        elif ext == '.pdf':
            # PDF - render each page as image using PyMuPDF
            if PYMUPDF_AVAILABLE:
                try:
                    pdf_doc = fitz.open(doc_path)
                    num_pages = len(pdf_doc)

                    for page_num in range(min(num_pages, 20)):  # Limit to 20 pages
                        page = pdf_doc[page_num]

                        # Render page to image (2x zoom for quality)
                        mat = fitz.Matrix(2, 2)
                        pix = page.get_pixmap(matrix=mat)

                        # Convert to PIL Image then to bytes
                        img_data = pix.tobytes("png")
                        img_buffer = io.BytesIO(img_data)

                        # Calculate display size
                        aspect = pix.width / pix.height
                        display_width = max_img_width
                        display_height = display_width / aspect
                        if display_height > max_img_height:
                            display_height = max_img_height
                            display_width = display_height * aspect

                        # Add page break between PDF pages (not before first)
                        if page_num > 0:
                            elements.append(PageBreak())
                            elements.append(Paragraph(f"Document {doc_number}: {filename} (continued)",
                                                      self.styles['JadwaDocTitle']))

                        img = Image(img_buffer, width=display_width, height=display_height)
                        img.hAlign = 'CENTER'
                        elements.append(Spacer(1, 10))
                        elements.append(img)

                        # Page number indicator
                        elements.append(Paragraph(f"Page {page_num + 1} of {num_pages}",
                                                  self.styles['JadwaDocType']))

                    pdf_doc.close()

                except Exception as e:
                    print(f"Error rendering PDF {filename}: {e}")
                    elements.append(self._create_file_info_box(filename, ext, doc_path, "PDF Document"))
            else:
                # PyMuPDF not available - show info box
                elements.append(Spacer(1, 10))
                elements.append(self._create_file_info_box(filename, ext, doc_path, "PDF Document"))

        else:
            # Other document types - show info box
            elements.append(Spacer(1, 10))
            elements.append(self._create_file_info_box(filename, ext, doc_path, f"{ext.upper()[1:]} Document"))

        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(width="60%", thickness=1, color=JadwaColors.GRAY_PALE, hAlign='CENTER'))
        elements.append(Spacer(1, 15))

        return elements

    def _create_file_info_box(self, filename, ext, filepath, file_type):
        """Create a styled info box for non-image documents"""
        file_size = self._get_file_size_str(filepath)

        # Icon based on file type
        if ext == '.pdf':
            icon_color = JadwaColors.RED
            bg_color = colors.HexColor('#FEF2F2')
            icon_text = "PDF"
        elif ext in ['.doc', '.docx']:
            icon_color = JadwaColors.BLUE
            bg_color = colors.HexColor('#EFF6FF')
            icon_text = "DOC"
        elif ext in ['.xls', '.xlsx']:
            icon_color = JadwaColors.SUCCESS
            bg_color = colors.HexColor('#F0FDF4')
            icon_text = "XLS"
        else:
            icon_color = JadwaColors.GRAY
            bg_color = JadwaColors.OFF_WHITE
            icon_text = ext.upper()[1:3] if ext else "FILE"

        # Create the info box
        icon_style = ParagraphStyle(name='Icon', fontSize=24, fontName='Helvetica-Bold',
                                    textColor=icon_color, alignment=TA_CENTER)
        name_style = ParagraphStyle(name='FN', fontSize=11, fontName='Helvetica-Bold',
                                    textColor=JadwaColors.CHARCOAL, alignment=TA_CENTER)
        info_style = ParagraphStyle(name='FI', fontSize=9, textColor=JadwaColors.GRAY,
                                    alignment=TA_CENTER)

        box_content = [
            [Paragraph(icon_text, icon_style)],
            [Spacer(1, 5)],
            [Paragraph(filename, name_style)],
            [Paragraph(f"{file_type} • {file_size}", info_style)],
            [Spacer(1, 5)],
            [Paragraph(self._t("Original file attached to business plan",
                               "الملف الأصلي مرفق بخطة العمل"), info_style)]
        ]

        box = Table(box_content, colWidths=[self.content_width * 0.7])
        box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('BOX', (0, 0), (-1, -1), 2, icon_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        box.hAlign = 'CENTER'

        return box

    def add_appendix(self, photos=None, documents=None, bplan_id=None):
        """Add appendix with embedded images and document info boxes"""
        if not photos and not documents:
            return

        self.story.append(PageBreak())
        self.story.append(Paragraph(self._t("Appendix: Supporting Documents", "الملحق: المستندات الداعمة"),
                                    ParagraphStyle(name='AppT', fontSize=22, textColor=JadwaColors.CHARCOAL,
                                                   fontName='Helvetica-Bold', alignment=TA_CENTER, spaceBefore=20,
                                                   spaceAfter=30)))

        doc_counter = 1

        # Photos section
        if photos:
            self.story.append(HRFlowable(width="100%", thickness=3, color=JadwaColors.BLUE,
                                         spaceBefore=10, spaceAfter=0, hAlign='LEFT'))
            self.story.append(Paragraph(self._t("Business Premises Photos", "صور مقر العمل"),
                                        self.styles['JadwaH1']))

            for photo in photos:
                fn = photo.get('premises_photo_filename', '') if isinstance(photo, dict) else getattr(photo,
                                                                                                      'premises_photo_filename',
                                                                                                      '')
                if fn and bplan_id:
                    for p in [f'apps/static/uploads/{bplan_id}/{fn}', f'static/uploads/{bplan_id}/{fn}']:
                        if os.path.exists(p):
                            elements = self._embed_document(p, fn, "Business Premises Photo", doc_counter)
                            for el in elements:
                                self.story.append(el)
                            doc_counter += 1
                            break

        # Documents section
        if documents:
            self.story.append(PageBreak())
            self.story.append(HRFlowable(width="100%", thickness=3, color=JadwaColors.BLUE,
                                         spaceBefore=10, spaceAfter=0, hAlign='LEFT'))
            self.story.append(Paragraph(self._t("Supporting Documents", "المستندات الداعمة"),
                                        self.styles['JadwaH1']))

            for doc in documents:
                fn = doc.get('premises_doc_filename', '') if isinstance(doc, dict) else getattr(doc,
                                                                                                'premises_doc_filename',
                                                                                                '')
                desc = doc.get('description', '') if isinstance(doc, dict) else getattr(doc, 'description', '')

                if fn and bplan_id:
                    # Try multiple paths
                    found = False
                    for p in [f'apps/static/uploads/docs/{bplan_id}/{fn}',
                              f'static/uploads/docs/{bplan_id}/{fn}',
                              f'apps/static/uploads/{bplan_id}/{fn}',
                              f'static/uploads/{bplan_id}/{fn}']:
                        if os.path.exists(p):
                            elements = self._embed_document(p, fn, desc, doc_counter)
                            for el in elements:
                                self.story.append(el)
                            doc_counter += 1
                            found = True
                            break

                    if not found:
                        # File not found - show placeholder
                        self.story.append(Paragraph(f"Document {doc_counter}: {fn}", self.styles['JadwaDocTitle']))
                        if desc:
                            self.story.append(Paragraph(desc, self.styles['JadwaDocDesc']))
                        self.story.append(Paragraph("[File not found on server]",
                                                    ParagraphStyle(name='NF', fontSize=10, textColor=JadwaColors.GRAY,
                                                                   alignment=TA_CENTER)))
                        self.story.append(Spacer(1, 20))
                        doc_counter += 1

    def build(self):
        doc = SimpleDocTemplate(self.filename, pagesize=A4, leftMargin=self.left_margin, rightMargin=self.right_margin,
                                topMargin=self.top_margin, bottomMargin=self.bottom_margin)
        doc.build(self.story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        return self.filename

    def _add_footer(self, canvas, doc):
        canvas.saveState()
        page_num = canvas.getPageNumber()
        if page_num > 1:
            canvas.setStrokeColor(JadwaColors.GRAY_PALE)
            canvas.line(self.left_margin, self.bottom_margin - 20, self.page_width - self.right_margin,
                        self.bottom_margin - 20)
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(JadwaColors.GRAY)
            canvas.drawCentredString(self.page_width / 2, self.bottom_margin - 35, str(page_num))
            canvas.setFont('Helvetica', 8)
            canvas.drawString(self.left_margin, self.bottom_margin - 35, self.business_name)
            canvas.drawRightString(self.page_width - self.right_margin, self.bottom_margin - 35, "JadwaPlan")
        canvas.restoreState()


def _get_attr(obj, key, default=''):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def _convert_quality(q):
    return {'High quality': 5, 'Good quality': 4, 'Consistent': 3, 'Commercial': 2}.get(q, 2)

def _convert_years(y):
    return {'10+': 5, '7-10': 4, '5-7': 3, '3-5': 2, '1-3': 1, '0-1': 0.5}.get(str(y), 1)

def _convert_price(p):
    return {'Very low': 5, 'Affordable': 4, 'Moderate': 3, 'Expensive': 2, 'Very expensive': 1}.get(p, 3)

def _convert_quantity(q):
    return {'Consistent': 5, 'Inconsistent': 2}.get(q, 3)


def generate_business_plan_pdf(data, output_path, lang='en'):
    logo_path = None
    for p in ['apps/static/assets/img/jadwaplan_logo.png',
              'apps/static/assets/img/Jadwa_plan_logo_final_version_-_transp-01.png']:
        if os.path.exists(p):
            logo_path = p
            break

    pdf = JadwaPlanPDF(output_path, lang=lang, logo_path=logo_path)
    t = lambda en, ar: ar if lang == 'ar' else en

    bplan_list = data.get('data_bplan', [{}])
    business_name = _get_attr(bplan_list[0], 'name', 'Business Plan') if bplan_list else 'Business Plan'

    ep_list = data.get('data_ep', [])
    ep = ep_list[0] if ep_list else {}
    if not isinstance(ep, dict):
        ep = {attr: getattr(ep, attr, '') for attr in dir(ep) if not attr.startswith('_')}

    pdf.add_cover_page(business_name)

    # TOC
    sections = []
    if ep.get('mission') or ep.get('vision') or ep.get('objectives'):
        sections.append(t("Mission, Vision & Objectives", "المهمة والرؤية والأهداف"))
    if ep.get('client_profile'):
        sections.append(t("Client's Profile", "ملف العميل"))
    if ep.get('business_profile'):
        sections.append(t("Business Profile", "ملف الأعمال"))
    if ep.get('business_premises'):
        sections.append(t("Business Premises", "مقر الأعمال"))
    if ep.get('market_analysis'):
        sections.append(t("Market Analysis", "تحليل السوق"))
    if ep.get('buz_suppliers') or ep.get('buz_production'):
        sections.append(t("Operations Plan", "خطة التشغيل"))
    if ep.get('requested_fund'):
        sections.append(t("Requested Fund", "التمويل المطلوب"))
    if ep.get('feasibility'):
        sections.append(t("Financial Feasibility", "الجدوى المالية"))
    if data.get('data_photo') or data.get('data_bp_doc'):
        sections.append(t("Appendix: Supporting Documents", "الملحق: المستندات الداعمة"))

    if sections:
        pdf.add_table_of_contents(sections)

    pdf.add_mvo_section(ep.get('mission', ''), ep.get('vision', ''), ep.get('objectives', ''))

    # Client Profile
    if ep.get('client_profile'):
        pdf.add_section(t("Client's Profile", "ملف العميل"), new_page=True)
        pdf.add_text(ep.get('client_profile', ''))

        # Experience with chart
        if ep.get('client_experiences'):
            pdf.add_subsection(t("Experiences", "الخبرات"))
            pdf.add_text(ep.get('client_experiences', ''))

        experiences = data.get('data_experiences', [])
        if experiences:
            labels = [_get_attr(e, 'field') for e in experiences if _get_attr(e, 'field')]
            values = [int(_get_attr(e, 'years_of_experience', 0)) for e in experiences if _get_attr(e, 'field')]
            if labels and values:
                pdf.add_horizontal_bar_chart(t("Career Experience", "الخبرة المهنية"), labels, values)

        # Partners with ownership chart
        if ep.get('client_partners'):
            pdf.add_subsection(t("Partners", "الشركاء"))
            pdf.add_text(ep.get('client_partners', ''))

        partners = data.get('data_partners', [])
        if partners:
            partners_total = sum(int(_get_attr(p, 'partner_shares', 0)) for p in partners)
            client_share = 100 - partners_total
            client_name = _get_attr(ep, 'full_name', '') or 'Owner'

            owner_data = [{'name': client_name, 'shares': client_share}]
            for p in partners:
                owner_data.append({
                    'name': _get_attr(p, 'partner_name', 'Partner'),
                    'shares': int(_get_attr(p, 'partner_shares', 0))
                })
            pdf.add_ownership_chart(t("Ownership Structure", "هيكل الملكية"), owner_data)

        expenses = data.get('data_ex', [])
        if expenses:
            pdf.add_subsection(t("Living Expenses", "المصاريف المعيشية"))
            headers = [t("Type", "النوع"), t("Value", "القيمة"), t("Period", "الفترة")]
            exp_data = []
            for e in expenses:
                period = t("Yearly", "سنوي") if _get_attr(e, 'unit') == 1 else t("Monthly", "شهري")
                exp_data.append([_get_attr(e, 'living_expenses'), f"${_get_attr(e, 'value', 0):,}", period])
            pdf.add_table(headers, exp_data)
            pdf.add_summary_table(t("Total Yearly Expenses", "إجمالي المصاريف السنوية"),
                                  f"${data.get('data_x_total', 0):,}", True)

            # Expenses pie chart
            labels = [_get_attr(e, 'living_expenses') for e in expenses]
            values = [_get_attr(e, 'total_value', _get_attr(e, 'value', 0)) for e in expenses]
            if any(values):
                pdf.add_pie_chart(t("Expenses Breakdown", "توزيع المصاريف"), labels, values)

        if ep.get('client_expenses'):
            pdf.add_text(ep.get('client_expenses', ''))
        if ep.get('client_employed'):
            pdf.add_subsection(t("Current Employment", "العمل الحالي"))
            pdf.add_text(ep.get('client_employed', ''))

    # Business Profile
    if ep.get('business_profile'):
        pdf.add_section(t("Business Profile", "ملف الأعمال"), new_page=True)
        pdf.add_text(ep.get('business_profile', ''))
        if ep.get('buz_product_services'):
            pdf.add_subsection(t("Products & Services", "المنتجات والخدمات"))
            pdf.add_text(ep.get('buz_product_services', ''))

        staff = data.get('data_staff', [])
        if staff:
            pdf.add_subsection(t("Staff", "فريق العمل"))
            headers = [t("Position", "المنصب"), t("Type", "النوع"), t("Salary", "الراتب")]
            staff_data = [
                [_get_attr(s, 'staff_position'), _get_attr(s, 'work_time'), f"${_get_attr(s, 'staff_salary', 0):,}"] for
                s in staff]
            pdf.add_table(headers, staff_data)
            pdf.add_summary_table(t("Total Annual Salaries", "إجمالي الرواتب السنوية"),
                                  f"${data.get('data_bs_total', 0):,}", True)
        if ep.get('buz_staff'):
            pdf.add_text(ep.get('buz_staff', ''))

        resources = data.get('data_br', [])
        if resources:
            pdf.add_subsection(t("Resources", "الموارد"))
            labels = [_get_attr(r, 'resource_subtype') for r in resources]
            values = [_get_attr(r, 'resource_value', 0) for r in resources]
            if any(values):
                pdf.add_pie_chart(t("Resource Distribution", "توزيع الموارد"), labels, values)
            if ep.get('buz_resource'):
                pdf.add_text(ep.get('buz_resource', ''))

        financial = data.get('data_fin', [])
        if financial:
            pdf.add_subsection(t("Financial History", "التاريخ المالي"))
            if ep.get('financial_history'):
                pdf.add_text(ep.get('financial_history', ''))
            labels = [str(_get_attr(f, 'financial_year')) for f in financial]
            datasets = [
                {'label': t('Sales', 'المبيعات'), 'data': [_get_attr(f, 'financial_sales', 0) for f in financial]},
                {'label': t('Profit', 'الربح'), 'data': [_get_attr(f, 'financial_profit', 0) for f in financial]}]
            pdf.add_bar_chart(t("Sales & Profit History", "تاريخ المبيعات والأرباح"), labels, datasets)

        if ep.get('source_of_funding'):
            pdf.add_subsection(t("Source of Funding", "مصادر التمويل"))
            pdf.add_text(ep.get('source_of_funding', ''))

    # Business Premises
    if ep.get('business_premises'):
        pdf.add_section(t("Business Premises", "مقر الأعمال"), new_page=True)
        pdf.add_text(ep.get('business_premises', ''))

        photos = data.get('data_photo', [])
        bplan_id = data.get('bplan_id', '')
        if photos and bplan_id:
            image_paths = []
            for photo in photos:
                fn = _get_attr(photo, 'premises_photo_filename')
                if fn:
                    for p in [f'apps/static/uploads/{bplan_id}/{fn}', f'static/uploads/{bplan_id}/{fn}']:
                        if os.path.exists(p):
                            image_paths.append(p)
                            break
            if image_paths:
                pdf.add_subsection(t("Photos", "الصور"))
                pdf.add_image_gallery(image_paths)

    # Market Analysis
    if ep.get('market_analysis'):
        pdf.add_section(t("Market Analysis", "تحليل السوق"), new_page=True)

        segments = data.get('data_mkt_segments', [])
        if segments and _get_attr(segments[0], 'segment_name'):
            pdf.add_subsection(t("Market Segments", "شرائح السوق"))
            labels = [_get_attr(s, 'segment_name') for s in segments]
            values = [_get_attr(s, 'segment_percentage', 0) for s in segments]
            pdf.add_pie_chart(t("Segment Distribution", "توزيع الشرائح"), labels, values)

        pdf.add_text(ep.get('market_analysis', ''))

        preferences = data.get('data_comp_preferences', [])
        if preferences:
            pdf.add_subsection(t("Customer Preferences", "تفضيلات العملاء"))
            comp_data = data.get('data_compname', [])
            comp = comp_data[0] if comp_data else {}
            if not isinstance(comp, dict):
                comp = {attr: getattr(comp, attr, '') for attr in dir(comp) if not attr.startswith('_')}

            labels = [_get_attr(p, 'preference') for p in preferences]
            datasets = [
                {'label': business_name, 'data': [_get_attr(p, 'preference_value', 0) for p in preferences]},
                {'label': comp.get('competitor_name_1st', 'Competitor 1'),
                 'data': [_get_attr(p, 'competitor1_value', 0) for p in preferences]},
                {'label': comp.get('competitor_name_2nd', 'Competitor 2'),
                 'data': [_get_attr(p, 'competitor2_value', 0) for p in preferences]},
                {'label': comp.get('competitor_name_3rd', 'Competitor 3'),
                 'data': [_get_attr(p, 'competitor3_value', 0) for p in preferences]}]
            pdf.add_bar_chart(t("Preference Comparison", "مقارنة التفضيلات"), labels, datasets)

    # Operations
    # Operations
    if ep.get('buz_suppliers') or ep.get('buz_production') or ep.get('buz_distribution'):
            pdf.add_section(t("Operations Plan", "خطة التشغيل"), new_page=True)

            if ep.get('buz_suppliers'):
                pdf.add_subsection(t("Suppliers", "الموردون"))
                pdf.add_text(ep.get('buz_suppliers', ''))

            # Supplier Radar Chart
            suppliers = data.get('data_suppliers', [])
            if suppliers and len(suppliers) > 1:
                categories = [t('Quality', 'الجودة'), t('Years', 'السنوات'), t('Price', 'السعر'),
                              t('Consistency', 'الاتساق')]
                datasets = []
                for supplier in suppliers[:4]:
                    products = supplier.get('products', [])
                    avg_price = sum(_convert_price(_get_attr(p, 'prices', 'Moderate')) for p in products) / len(
                        products) if products else 3
                    avg_qty = sum(_convert_quantity(_get_attr(p, 'quantity', 'Consistent')) for p in products) / len(
                        products) if products else 3
                    values = [
                        _convert_quality(_get_attr(supplier, 'quality', 'Commercial')),
                        _convert_years(_get_attr(supplier, 'years_of_collaboration', '1-3')),
                        avg_price,
                        avg_qty
                    ]
                    datasets.append({'label': _get_attr(supplier, 'supplier_name', 'Supplier'), 'data': values})

                if datasets:
                    pdf.add_radar_chart(t("Supplier Comparison", "مقارنة الموردين"), categories, datasets)

            if ep.get('buz_production'):
                pdf.add_subsection(t("Production", "الإنتاج"))
                pdf.add_text(ep.get('buz_production', ''))

            # Capacity Gauge
            production = data.get('data_production', [])
            if production:
                prod = production[0]
                current = float(_get_attr(prod, 'current_capacity', 0))
                maximum = float(_get_attr(prod, 'max_expected_capacity', 0))
                if maximum > 0:
                    pdf.add_gauge_chart(t("Capacity Utilization", "استغلال الطاقة"), current, maximum)
                    unit = _get_attr(prod, 'production_unit', 'units')
                    tf = _get_attr(prod, 'time_frame', 'month')
                    pdf.add_text(f"Current: {current:.0f} {unit}/{tf} | Maximum: {maximum:.0f} {unit}/{tf}")

            if ep.get('buz_distribution'):
                pdf.add_subsection(t("Distribution", "التوزيع"))
                pdf.add_text(ep.get('buz_distribution', ''))

            # Supply Chain Summary Table
            distribution = data.get('data_distribution', [])
            if suppliers or production or distribution:
                pdf.add_subsection(t("Supply Chain Summary", "ملخص سلسلة التوريد"))
                total_products = sum(len(s.get('products', [])) for s in suppliers) if suppliers else 0
                headers = [t("Component", "المكون"), t("Count", "العدد"), t("Details", "التفاصيل")]
                chain_data = [
                    [t("Suppliers", "الموردون"), str(len(suppliers) if suppliers else 0),
                     ', '.join(_get_attr(s, 'supplier_name', '') for s in (suppliers or [])[:3])],
                    [t("Products/Services", "المنتجات/الخدمات"), str(total_products),
                     t("From suppliers", "من الموردين")],
                    [t("Production Lines", "خطوط الإنتاج"), str(len(production) if production else 0), '-'],
                    [t("Distribution Channels", "قنوات التوزيع"), str(len(distribution) if distribution else 0),
                     ', '.join(_get_attr(d, 'type', '') for d in (distribution or [])[:3])]
                ]
                pdf.add_table(headers, chain_data)

    # Requested Fund
    if ep.get('requested_fund'):
        pdf.add_section(t("Requested Fund", "التمويل المطلوب"), new_page=True)
        pdf.add_text(ep.get('requested_fund', ''))

        items = []
        for item in data.get('data_machines', []):
            items.append([f"{t('Machinery', 'آلات')} - {_get_attr(item, 'item')}",
                          f"{_get_attr(item, 'quantity')} {_get_attr(item, 'unit')}",
                          f"${_get_attr(item, 'total_cost', 0):,}"])
        for item in data.get('data_installation', []):
            items.append([t('Installation', 'تركيب'), '-', f"${_get_attr(item, 'total_cost', 0):,}"])
        for item in data.get('data_materials', []):
            items.append([f"{t('Materials', 'مواد')} - {_get_attr(item, 'item')}",
                          f"{_get_attr(item, 'quantity')} {_get_attr(item, 'unit')}",
                          f"${_get_attr(item, 'total_cost', 0):,}"])
        for item in data.get('data_salaries', []):
            items.append([f"{t('Salaries', 'رواتب')} - {_get_attr(item, 'item')}", '-',
                          f"${_get_attr(item, 'total_cost', 0):,}"])
        for item in data.get('data_ocosts', []):
            items.append([f"{t('Other', 'أخرى')} - {_get_attr(item, 'item')}",
                          f"{_get_attr(item, 'quantity')} {_get_attr(item, 'unit')}",
                          f"${_get_attr(item, 'total_cost', 0):,}"])

        if items:
            pdf.add_subsection(t("Fund Breakdown", "تفاصيل التمويل"))
            pdf.add_table([t("Item", "البند"), t("Details", "التفاصيل"), t("Total", "الإجمالي")], items)
            pdf.add_summary_table(t("Total Requested Fund", "إجمالي التمويل المطلوب"),
                                  f"${data.get('data_fund_total', 0):,}", True)

    # Feasibility
    if ep.get('feasibility'):
        pdf.add_section(t("Financial Feasibility", "الجدوى المالية"), new_page=True)
        pdf.add_text(ep.get('feasibility', ''))

        projections = data.get('data_projections', [])
        total_projections = data.get('data_total_projections', {})
        if projections and total_projections:
            pdf.add_projections_table(projections, total_projections, data.get('current_inflation_rate', 3.0))

    # Appendix with embedded documents
    pdf.add_appendix(photos=data.get('data_photo', []), documents=data.get('data_bp_doc', []),
                     bplan_id=data.get('bplan_id', ''))

    return pdf.build()