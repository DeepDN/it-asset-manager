#!/bin/bash

# PostgreSQL backup script for IT Asset Manager
# This script creates automated backups of the PostgreSQL database

set -e

# Configuration
DB_HOST="postgres"
DB_NAME="it_assets_prod"
DB_USER="it_assets_user"
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/it_assets_backup_${TIMESTAMP}.sql"
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to create backup
create_backup() {
    log "Starting database backup..."
    
    # Create SQL dump
    pg_dump -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" \
        --no-password \
        --verbose \
        --clean \
        --if-exists \
        --create \
        --format=custom \
        --file="${BACKUP_FILE}.custom"
    
    # Create plain SQL backup as well
    pg_dump -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" \
        --no-password \
        --verbose \
        --clean \
        --if-exists \
        --create \
        --format=plain \
        --file="${BACKUP_FILE}"
    
    # Compress the plain SQL backup
    gzip "${BACKUP_FILE}"
    
    log "Backup created: ${BACKUP_FILE}.gz and ${BACKUP_FILE}.custom"
}

# Function to cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than ${RETENTION_DAYS} days..."
    
    find "${BACKUP_DIR}" -name "it_assets_backup_*.sql.gz" -mtime +${RETENTION_DAYS} -delete
    find "${BACKUP_DIR}" -name "it_assets_backup_*.custom" -mtime +${RETENTION_DAYS} -delete
    
    log "Cleanup completed"
}

# Function to verify backup
verify_backup() {
    local backup_file="$1"
    
    if [ -f "${backup_file}" ]; then
        local size=$(stat -f%z "${backup_file}" 2>/dev/null || stat -c%s "${backup_file}" 2>/dev/null)
        if [ "${size}" -gt 1000 ]; then
            log "Backup verification successful: ${backup_file} (${size} bytes)"
            return 0
        else
            log "ERROR: Backup file is too small: ${backup_file} (${size} bytes)"
            return 1
        fi
    else
        log "ERROR: Backup file not found: ${backup_file}"
        return 1
    fi
}

# Main backup process
main() {
    log "Starting backup process for database: ${DB_NAME}"
    
    # Wait for database to be ready
    until pg_isready -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}"; do
        log "Waiting for database to be ready..."
        sleep 5
    done
    
    # Create backup
    if create_backup; then
        # Verify backups
        if verify_backup "${BACKUP_FILE}.gz" && verify_backup "${BACKUP_FILE}.custom"; then
            log "Backup process completed successfully"
            
            # Cleanup old backups
            cleanup_old_backups
            
            # Send notification (if configured)
            if [ -n "${WEBHOOK_URL}" ]; then
                curl -X POST "${WEBHOOK_URL}" \
                    -H "Content-Type: application/json" \
                    -d "{\"text\":\"IT Asset Manager backup completed successfully at $(date)\"}" \
                    || log "Failed to send notification"
            fi
        else
            log "ERROR: Backup verification failed"
            exit 1
        fi
    else
        log "ERROR: Backup creation failed"
        exit 1
    fi
}

# Run backup if called directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
