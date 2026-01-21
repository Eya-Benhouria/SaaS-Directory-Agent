import clsx from 'clsx';
import type { SubmissionStatus } from '../types';

interface StatusBadgeProps {
  status: SubmissionStatus;
  className?: string;
}

const statusConfig: Record<SubmissionStatus, { label: string; className: string }> = {
  pending: { label: 'Pending', className: 'bg-yellow-100 text-yellow-800' },
  in_progress: { label: 'In Progress', className: 'bg-purple-100 text-purple-800' },
  submitted: { label: 'Submitted', className: 'bg-blue-100 text-blue-800' },
  approved: { label: 'Approved', className: 'bg-green-100 text-green-800' },
  rejected: { label: 'Rejected', className: 'bg-red-100 text-red-800' },
  failed: { label: 'Failed', className: 'bg-red-100 text-red-800' },
  requires_review: { label: 'Needs Review', className: 'bg-orange-100 text-orange-800' },
};

export default function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status] || { label: status, className: 'bg-gray-100 text-gray-800' };

  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        config.className,
        className
      )}
    >
      {config.label}
    </span>
  );
}
