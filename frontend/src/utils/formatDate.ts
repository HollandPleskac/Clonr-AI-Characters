export function formatDate(date: Date): string {
  const diffInMilliseconds = Date.now() - date.getTime();
  const diffInMinutes = Math.floor(diffInMilliseconds / (1000 * 60));
  const diffInHours = Math.floor(diffInMilliseconds / (1000 * 60 * 60));

  // If difference is less than 1 minute, return an empty string
  if (diffInMinutes < 1) {
    return 'a few seconds ago';
  }

  // If difference is less than 30 minutes, return in minutes
  if (diffInMinutes < 30) {
    return `${diffInMinutes}m`;
  }

  // If difference is less than 24 hours, return in hours
  if (diffInHours < 24) {
    return `${diffInHours}h`;
  }

  // Format date if it's more than 24 hours ago
  const day = date.getDate();
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const month = monthNames[date.getMonth()];

  return `${day} ${month}`;
}