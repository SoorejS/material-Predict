"""
CCIE Elite Detailed Exporter (V7.0)
Generates high-fidelity PDF and multi-sheet Excel reports with full dimension specifics.
"""

import pandas as pd
from fpdf import FPDF
import datetime

class EliteExporter:
    """
    Industry-ready exporter for deep-dimensioned construction reports.
    """
    def __init__(self, report: dict, plot_w: float, plot_l: float):
        self.report = report
        self.plot_w = plot_w
        self.plot_l = plot_l
        self.currency = report.get("currency", "USD")
        
    def generate_excel(self, filename: str = "Elite_Construction_BOQ.xlsx") -> str:
        """
        Generates a 3-sheet Excel report: 
        1. Dimension Audit, 2. Material-Specific Costing, 3. Optimization Summary.
        """
        # Sheet 1: Project Dimensions & Geometry Audit
        dim_data = [
            {"Property": "Plot Width", "Value": f"{self.plot_w} ft"},
            {"Property": "Plot Length", "Value": f"{self.plot_l} ft"},
            {"Property": "Built Area", "Value": f"{self.report['built_area_sqft']} sqft"},
            {"Property": "Soil Type", "Value": self.report.get("soil_type", "Standard").upper()}
        ]
        df_dim = pd.DataFrame(dim_data)
        
        # Sheet 2: Material-Specific Segment Costing (The "Real" BOQ)
        seg_data = []
        for name, data in self.report["segments"].items():
            row = {
              "Phase Segment": name,
              "Phase Timeline": data.get("phase", "N/A"),
              "Cost Detail": f"{self.currency} {data['cost']:,}"
            }
            # Append dynamic and material-specific attributes if present
            for k, v in data.items():
                if k not in ["cost", "phase"]:
                    row[k.replace("_", " ").capitalize()] = v
            seg_data.append(row)
        df_seg = pd.DataFrame(seg_data)
        
        # Sheet 3: Financial Optimization Report
        df_opt = pd.DataFrame(self.report.get("optimizations", []))
        
        with pd.ExcelWriter(filename) as writer:
            df_dim.to_excel(writer, sheet_name='Dimensions Audit', index=False)
            df_seg.to_excel(writer, sheet_name='Material-Specific BOQ', index=False)
            df_opt.to_excel(writer, sheet_name='Optimization Advice', index=False)
            
        return filename

    def generate_pdf(self, filename: str = "Elite_Construction_Report.pdf") -> str:
        """
        Generates a professional executive-ready PDF report.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        
        # Header
        pdf.cell(200, 10, txt="🏢 CCIE ELITE: PHASED BOQ & FINANCIAL REPORT", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
        pdf.ln(10)
        
        # Summary Box
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"1. Executive Financial Summary", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(200, 8, txt=f"Total Cost Estimate: {self.currency} {self.report['total_cost']:,}", ln=True)
        pdf.cell(200, 8, txt=f"Built Area: {self.report['built_area_sqft']} sqft", ln=True)
        pdf.cell(200, 8, txt=f"Confidence Level: {self.report['uncertainty']['confidence_pct']}%", ln=True)
        pdf.ln(10)
        
        # Segment and Detailed Material Breakdown
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"2. Dimension & Material-Specific Segment Analysis", ln=True)
        pdf.set_font("Arial", size=9)
        
        for name, data in self.report["segments"].items():
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(200, 8, txt=f"➡ {name.upper()} ({data['phase']})", ln=True)
            pdf.set_font("Arial", size=9)
            details = ", ".join([f"{k}: {v}" for k,v in data.items() if k not in ["cost", "phase"]])
            pdf.cell(200, 8, txt=f"   Properties: {details}", ln=True)
            pdf.cell(200, 8, txt=f"   Segment Cost: {self.currency} {data['cost']:,}", ln=True)
            pdf.ln(2)
            
        pdf.ln(10)
        # Optimizations
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"3. Strategic Optimizations (Applied Thinking)", ln=True)
        pdf.set_font("Arial", size=9)
        for opt in self.report.get("optimizations", []):
            pdf.cell(200, 8, txt=f"⭐ {opt['action']} | Savings: {opt['est_saving']}", ln=True)
            
        pdf.output(filename)
        return filename

if __name__ == "__main__":
    rep = {
        "built_area_sqft": 1000, 
        "total_cost": 1500000, 
        "currency": "INR",
        "uncertainty": {"confidence_pct": 92.5},
        "segments": {
            "Foundation": {"phase": "Month 1", "cost": 300000, "cement_bags": 120}
        },
        "optimizations": [{"action": "Wall Thinning", "est_saving": "₹65,000"}]
    }
    ex = EliteExporter(rep, 20, 30)
    ex.generate_excel()
    ex.generate_pdf()
