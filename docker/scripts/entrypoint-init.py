"""Database initialization script for Docker entrypoint."""
import os
import sys
import time

DATABASE_URL = os.environ.get('DATABASE_URL', '')


def wait_for_postgres():
    """Wait for PostgreSQL to become available."""
    if not DATABASE_URL.startswith('postgresql'):
        print('Using SQLite - no wait needed')
        return

    print('PostgreSQL detected. Waiting for database...')
    for i in range(30):
        try:
            import psycopg2
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            print('PostgreSQL is ready!')
            return
        except Exception as e:
            print(f'Waiting for PostgreSQL... ({i+1}/30) - {e}')
            time.sleep(2)

    print('ERROR: PostgreSQL did not become ready')
    sys.exit(1)


def init_database():
    """Initialize database tables and seed admin user."""
    print('Initializing database...')
    os.environ.setdefault('FLASK_ENV', 'production')
    sys.path.insert(0, '/app')

    # We need to import and create the app within app context
    from it_asset_manager.core.app import create_app
    from it_asset_manager.core.database import db

    app = create_app()
    with app.app_context():
        from it_asset_manager.models.user import User
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User()
            admin.username = 'admin'
            admin.email = 'admin@assetpulse.local'
            admin.role = 'super_admin'
            admin.department = 'IT'
            admin.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin)
            db.session.commit()
            print('Admin user created: admin / ' + os.environ.get('ADMIN_PASSWORD', 'admin123'))
        else:
            if admin.role != 'super_admin':
                admin.role = 'super_admin'
                db.session.commit()
                print('Admin role upgraded to super_admin')
            print('Admin user already exists')
        print('Database initialization complete')


if __name__ == '__main__':
    wait_for_postgres()
    init_database()
