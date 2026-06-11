from flask import Blueprint, render_template, jsonify, flash
from flask_login import login_required
from ..services.report_service import ReportService

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/dashboard')
@login_required
def executive_dashboard():
    try:
        data = ReportService.get_executive_dashboard()
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        data = {}
    return render_template('reports/dashboard.html', data=data)


@reports_bp.route('/warranty')
@login_required
def warranty_report():
    try:
        data = ReportService.get_warranty_report()
    except Exception as e:
        flash(f'Error loading warranty report: {str(e)}', 'error')
        data = []
    return render_template('reports/warranty.html', items=data)


@reports_bp.route('/financial')
@login_required
def financial_report():
    try:
        data = ReportService.get_financial_report()
    except Exception as e:
        flash(f'Error loading financial report: {str(e)}', 'error')
        data = {}
    return render_template('reports/financial.html', data=data)


@reports_bp.route('/audit')
@login_required
def audit_report():
    try:
        data = ReportService.get_audit_report()
    except Exception as e:
        flash(f'Error loading audit report: {str(e)}', 'error')
        data = {}
    return render_template('reports/audit.html', data=data)


@reports_bp.route('/utilization')
@login_required
def utilization_report():
    try:
        data = ReportService.get_utilization_report()
    except Exception as e:
        flash(f'Error loading utilization report: {str(e)}', 'error')
        data = {}
    return render_template('reports/utilization.html', data=data)


@reports_bp.route('/api/executive')
@login_required
def api_executive():
    try:
        return jsonify(ReportService.get_executive_dashboard())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
