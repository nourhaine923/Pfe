# app/routers/export_routes.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from bson import ObjectId
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
from app.database import db
from app.auth.dependencies import nephrologist_or_admin

router = APIRouter(prefix="/export", tags=["Export"])

def create_transplantation_pdf(transplantation_id: str):
    """Generate PDF for transplantation details"""
    tx = db["transplantations"].find_one({"_id": ObjectId(transplantation_id)})
    if not tx:
        raise HTTPException(404, "Transplantation not found")
    
    recipient = db["patients"].find_one({"_id": ObjectId(tx["recipient_id"])})
    donor = db["patients"].find_one({"_id": ObjectId(tx["donor_id"])})
    outcome = db["outcomes"].find_one({"transplantation_id": ObjectId(transplantation_id)})
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        alignment=1,
        spaceAfter=30
    )
    story.append(Paragraph("KTOuIP - Kidney Transplant Management", title_style))
    story.append(Paragraph(f"Transplantation Report - {tx.get('transplantNumber', 'N/A')}", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Transplant Info
    story.append(Paragraph("Transplant Information", styles['Heading3']))
    data = [
        ["Transplant Number", tx.get('transplantNumber', 'N/A')],
        ["Transplant Date", tx.get('transplantDate', 'N/A')],
        ["Location", tx.get('transplantLocation', 'N/A')],
        ["Status", tx.get('status', 'PENDING')],
        ["Cold Ischemia", f"{tx.get('coldIschemiaHours', 0)} hours"],
        ["Warm Ischemia", f"{tx.get('warmIschemiaMinutes', 0)} minutes"],
    ]
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Donor Info
    story.append(Paragraph("Donor Information", styles['Heading3']))
    if donor:
        data = [
            ["Name", f"{donor.get('firstName', '')} {donor.get('lastName', '')}"],
            ["Blood Group", donor.get('bloodGroup', 'N/A')],
            ["Donor Type", donor.get('donorType', 'N/A')],
            ["Age at Donation", donor.get('ageAtDonation', 'N/A')],
        ]
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(table)
    story.append(Spacer(1, 20))
    
    # Recipient Info
    story.append(Paragraph("Recipient Information", styles['Heading3']))
    if recipient:
        data = [
            ["Name", f"{recipient.get('firstName', '')} {recipient.get('lastName', '')}"],
            ["Blood Group", recipient.get('bloodGroup', 'N/A')],
            ["Birth Date", recipient.get('birthDate', 'N/A')],
        ]
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(table)
    story.append(Spacer(1, 20))
    
    # Pre-Transplant Assessment
    pre_tx = tx.get('preTransplantAssessment', {})
    if pre_tx:
        story.append(Paragraph("Pre-Transplant Assessment", styles['Heading3']))
        data = [
            ["Age at Transplant", f"{pre_tx.get('ageAtTransplant', 'N/A')} years"],
            ["Previous Transplants", pre_tx.get('numberOfPreviousTransplants', 0)],
            ["Nephropathy Type", pre_tx.get('nephropathyType', 'N/A')],
            ["EER Modality", pre_tx.get('eerModality', 'N/A')],
            ["Transplant Delay", f"{pre_tx.get('trDelayMonths', 0)} months"],
        ]
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
    
    # Outcome
    if outcome:
        story.append(Paragraph("Outcome", styles['Heading3']))
        status = ""
        if outcome.get('aliveWithFunctioningGraft'):
            status = "Alive with Functioning Graft"
        elif outcome.get('returnToDialysis'):
            status = "Return to Dialysis"
        elif outcome.get('deathWithFunctioningGraft'):
            status = "Death with Functioning Graft"
        data = [
            ["Last Follow-up", outcome.get('lastNewsDate', 'N/A')],
            ["Patient Status", status],
        ]
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(table)
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def create_followup_pdf(followup_id: str):
    """Generate PDF for follow-up details"""
    followup = db["followups"].find_one({"_id": ObjectId(followup_id)})
    if not followup:
        raise HTTPException(404, "Follow-up not found")
    
    tx = db["transplantations"].find_one({"_id": ObjectId(followup["transplantation_id"])})
    recipient = db["patients"].find_one({"_id": ObjectId(tx["recipient_id"])}) if tx else None
    
    # Get all related data
    vitals = db["vitals"].find_one({"followup_id": ObjectId(followup_id)})
    biological = db["biological_measurements"].find_one({"followup_id": ObjectId(followup_id)})
    immunological = list(db["immunological_markers"].find({"followup_id": ObjectId(followup_id)}))
    rejection = db["rejections"].find_one({"followup_id": ObjectId(followup_id)})
    adverse_events = list(db["adverse_events"].find({"followup_id": ObjectId(followup_id)}))
    treatments = list(db["treatments"].find({"followup_id": ObjectId(followup_id)}))
    immunosuppression = db["immunosuppression_regimens"].find_one({"followup_id": ObjectId(followup_id)})
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        alignment=1,
        spaceAfter=30
    )
    story.append(Paragraph("KTOuIP - Kidney Transplant Management", title_style))
    story.append(Paragraph(f"Follow-up Report", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Patient Info
    story.append(Paragraph("Patient Information", styles['Heading3']))
    if recipient:
        data = [
            ["Patient Name", f"{recipient.get('firstName', '')} {recipient.get('lastName', '')}"],
            ["Medical Record Number", recipient.get('medicalRecordNumber', 'N/A')],
            ["Transplant Number", tx.get('transplantNumber', 'N/A') if tx else 'N/A'],
            ["Visit Date", followup.get('visitDate', 'N/A')],
            ["Post-Transplant Day", followup.get('postTransplantDay', 'N/A')],
            ["Clinical Status", followup.get('clinicalStatus', 'N/A')],
        ]
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(table)
    story.append(Spacer(1, 20))
    
    # Vital Signs
    if vitals:
        story.append(Paragraph("Vital Signs", styles['Heading3']))
        data = [
            ["Date/Time", vitals.get('dateTime', 'N/A')],
            ["Heart Rate", f"{vitals.get('heartRate', 'N/A')} bpm"],
            ["Temperature", f"{vitals.get('temperature', 'N/A')} °C"],
            ["O2 Saturation", f"{vitals.get('oxygenSaturation', 'N/A')}%"],
            ["Urine Output", f"{vitals.get('urineOutputMl', 'N/A')} ml"],
            ["Blood Pressure", f"{vitals.get('bloodPressure', 'N/A')} mmHg"],
        ]
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
    
    # Biological Measurements
    if biological:
        story.append(Paragraph("Biological Measurements", styles['Heading3']))
        data = [
            ["Creatinine", f"{biological.get('creatinine', 'N/A')} mg/dL"],
            ["Urea", f"{biological.get('urea', 'N/A')} mg/dL"],
            ["eGFR", f"{biological.get('gfr', 'N/A')} mL/min"],
            ["Hemoglobin", f"{biological.get('hemoglobin', 'N/A')} g/dL"],
            ["CRP", f"{biological.get('crp', 'N/A')} mg/L"],
            ["Proteinuria", f"{biological.get('proteinuria', 'N/A')} mg/24h"],
        ]
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
    
    # Immunological Markers
    if immunological:
        story.append(Paragraph("Immunological Markers", styles['Heading3']))
        for marker in immunological:
            data = [
                ["Marker Type", marker.get('markerType', 'N/A')],
                ["Time Point", marker.get('timePoint', 'N/A')],
                ["Value", f"{marker.get('value', 'N/A')} {marker.get('unit', '')}"],
            ]
            table = Table(data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            story.append(table)
            story.append(Spacer(1, 10))
    
    # Rejection Episode
    if rejection:
        story.append(Paragraph("Rejection Episode", styles['Heading3']))
        data = [
            ["Date", rejection.get('date', 'N/A')],
            ["Type", rejection.get('type', 'N/A')],
            ["Grade", rejection.get('grade', 'N/A')],
            ["Biopsy Proven", "Yes" if rejection.get('biopsyProven') else "No"],
            ["Treatment", rejection.get('treatment', 'N/A')],
            ["Resolved", "Yes" if rejection.get('resolved') else "No"],
        ]
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
    
    # Adverse Events
    if adverse_events:
        story.append(Paragraph("Adverse Events", styles['Heading3']))
        for event in adverse_events:
            data = [
                ["Date", event.get('date', 'N/A')],
                ["Event Type", event.get('eventType', 'N/A')],
                ["Severity", event.get('severity', 'N/A')],
                ["Comment", event.get('comment', 'N/A')],
            ]
            table = Table(data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            story.append(table)
            story.append(Spacer(1, 10))
    
    # Immunosuppression Regimen
    if immunosuppression:
        story.append(Paragraph("Immunosuppression Regimen", styles['Heading3']))
        drugs = []
        if immunosuppression.get('corticosteroids'): drugs.append("Corticosteroids")
        if immunosuppression.get('tacrolimus'): drugs.append("Tacrolimus")
        if immunosuppression.get('ciclosporine'): drugs.append("Ciclosporine")
        if immunosuppression.get('mmf'): drugs.append("MMF")
        if immunosuppression.get('azathioprine'): drugs.append("Azathioprine")
        if immunosuppression.get('sirolimus'): drugs.append("Sirolimus")
        
        data = [
            ["Start Date", immunosuppression.get('startDate', 'N/A')],
            ["End Date", immunosuppression.get('endDate', 'Ongoing') or 'Ongoing'],
            ["Medications", ", ".join(drugs) if drugs else "None"],
        ]
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


# API Endpoints
@router.get("/transplantation/{transplantation_id}")
async def export_transplantation(transplantation_id: str, user=Depends(nephrologist_or_admin)):
    """Export transplantation details as PDF"""
    try:
        pdf_buffer = create_transplantation_pdf(transplantation_id)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=transplantation_{transplantation_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/followup/{followup_id}")
async def export_followup(followup_id: str, user=Depends(nephrologist_or_admin)):
    """Export follow-up details as PDF"""
    try:
        pdf_buffer = create_followup_pdf(followup_id)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=followup_{followup_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(500, str(e))