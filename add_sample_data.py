#!/usr/bin/env python3
"""
Sample data script for IT Asset Manager
Run this after setting up the application to add sample data for testing
"""

from app import app, db, Asset, ApplicationAccess, GitHubAccess
from datetime import datetime, date

def add_sample_data():
    with app.app_context():
        # Sample Assets
        assets = [
            Asset(
                asset_type='laptop',
                brand='Dell',
                model='Latitude 5520',
                serial_number='DL001234',
                processor='Intel i7-11800H',
                ram_gb=16,
                storage_gb=512,
                storage_type='SSD',
                assigned_to='John Doe',
                assign_date=date(2024, 1, 15),
                status='assigned',
                remarks='Primary development laptop'
            ),
            Asset(
                asset_type='desktop',
                brand='HP',
                model='EliteDesk 800',
                serial_number='HP005678',
                processor='Intel i5-12400',
                ram_gb=32,
                storage_gb=1000,
                storage_type='SSD',
                assigned_to='Jane Smith',
                assign_date=date(2024, 2, 1),
                status='assigned',
                remarks='Workstation for design team'
            ),
            Asset(
                asset_type='mobile',
                brand='Apple',
                model='iPhone 14',
                serial_number='IP789012',
                assigned_to='Mike Johnson',
                assign_date=date(2024, 3, 10),
                status='assigned',
                remarks='Company phone for sales team'
            ),
            Asset(
                asset_type='tablet',
                brand='Samsung',
                model='Galaxy Tab S8',
                serial_number='ST345678',
                status='unassigned',
                remarks='Available for assignment'
            ),
            Asset(
                asset_type='laptop',
                brand='Lenovo',
                model='ThinkPad X1',
                serial_number='LN901234',
                processor='Intel i7-12700U',
                ram_gb=16,
                storage_gb=512,
                storage_type='SSD',
                status='unassigned',
                remarks='New laptop ready for deployment'
            )
        ]

        # Sample Application Access
        app_accesses = [
            ApplicationAccess(
                user_name='John Doe',
                application_name='GitHub',
                access_level='Admin',
                assign_date=date(2024, 1, 15),
                status='active',
                remarks='Lead developer access'
            ),
            ApplicationAccess(
                user_name='Jane Smith',
                application_name='Google Workspace',
                access_level='Admin',
                assign_date=date(2024, 1, 20),
                status='active',
                remarks='HR department admin'
            ),
            ApplicationAccess(
                user_name='Mike Johnson',
                application_name='Slack',
                access_level='Write',
                assign_date=date(2024, 2, 1),
                status='active',
                remarks='Sales team communication'
            ),
            ApplicationAccess(
                user_name='Sarah Wilson',
                application_name='AWS Console',
                access_level='Read',
                assign_date=date(2024, 1, 10),
                remove_date=date(2024, 4, 15),
                status='revoked',
                remarks='Temporary access for project'
            ),
            ApplicationAccess(
                user_name='John Doe',
                application_name='Microsoft 365',
                access_level='Write',
                assign_date=date(2024, 1, 15),
                status='active',
                remarks='Office suite access'
            )
        ]

        # Sample GitHub Access
        github_accesses = [
            GitHubAccess(
                user_name='john.doe',
                organization_name='company-org',
                repo_name='main-application',
                access_type='Admin',
                assign_date=date(2024, 1, 15),
                status='active',
                remarks='Lead developer on main project'
            ),
            GitHubAccess(
                user_name='jane.smith',
                organization_name='company-org',
                repo_name='documentation',
                access_type='Write',
                assign_date=date(2024, 1, 20),
                status='active',
                remarks='Documentation maintainer'
            ),
            GitHubAccess(
                user_name='mike.johnson',
                organization_name='company-org',
                repo_name='sales-tools',
                access_type='Maintainer',
                assign_date=date(2024, 2, 1),
                status='active',
                remarks='Sales tools repository'
            ),
            GitHubAccess(
                user_name='sarah.wilson',
                organization_name='company-org',
                repo_name='temp-project',
                access_type='Read',
                assign_date=date(2024, 1, 10),
                remove_date=date(2024, 4, 15),
                status='revoked',
                remarks='Temporary project access'
            ),
            GitHubAccess(
                user_name='john.doe',
                organization_name='open-source-org',
                repo_name='community-project',
                access_type='Write',
                assign_date=date(2024, 3, 1),
                status='active',
                remarks='Open source contribution'
            )
        ]

        # Add all sample data
        try:
            for asset in assets:
                db.session.add(asset)
            
            for access in app_accesses:
                db.session.add(access)
            
            for github_access in github_accesses:
                db.session.add(github_access)
            
            db.session.commit()
            print("✅ Sample data added successfully!")
            print(f"   📱 Added {len(assets)} sample assets")
            print(f"   🔐 Added {len(app_accesses)} application access records")
            print(f"   🐙 Added {len(github_accesses)} GitHub access records")
            print("\n🎯 You can now explore the application with sample data!")
            
        except Exception as e:
            print(f"❌ Error adding sample data: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    print("🚀 Adding sample data to IT Asset Manager...")
    add_sample_data()
