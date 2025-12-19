#!/bin/bash

# Setup cron job for cleaning up expired temporary images
# This script should be run once during deployment

set -e

echo "Setting up cron job for expired image cleanup..."

# Get the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create a temporary cron file
CRON_FILE="/tmp/imagebed_cron"

# Get existing cron jobs
crontab -l > "$CRON_FILE" 2>/dev/null || true

# Check if cron job already exists
if grep -q "cleanup_expired_images" "$CRON_FILE"; then
    echo "Cron job already exists. Updating..."
    # Remove old cron job
    grep -v "cleanup_expired_images" "$CRON_FILE" > "${CRON_FILE}.tmp" || true
    mv "${CRON_FILE}.tmp" "$CRON_FILE"
fi

# Add new cron job (runs every hour)
# Note: Adjust the path if you're using Docker
if [ -f "/.dockerenv" ]; then
    # Running in Docker
    echo "0 * * * * cd /app && docker compose exec -T web python manage.py cleanup_expired_images >> /var/log/image_bed_cleanup.log 2>&1" >> "$CRON_FILE"
else
    # Running directly on host
    echo "0 * * * * cd $PROJECT_DIR && python manage.py cleanup_expired_images >> /var/log/image_bed_cleanup.log 2>&1" >> "$CRON_FILE"
fi

# Install the cron job
crontab "$CRON_FILE"

# Clean up
rm "$CRON_FILE"

echo "✅ Cron job installed successfully!"
echo "The cleanup task will run every hour at minute 0"
echo "Logs will be written to: /var/log/image_bed_cleanup.log"
echo ""
echo "To view the cron job: crontab -l"
echo "To remove the cron job: crontab -e (then delete the line)"
echo ""
echo "You can manually run the cleanup command:"
echo "  docker compose exec web python manage.py cleanup_expired_images"
echo ""
echo "Or with dry-run to see what would be deleted:"
echo "  docker compose exec web python manage.py cleanup_expired_images --dry-run"
