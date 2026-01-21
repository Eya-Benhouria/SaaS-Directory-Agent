import {
    ArrowLeftIcon,
    ArrowPathIcon,
    ArrowTopRightOnSquareIcon,
    CheckCircleIcon,
    PlayIcon,
    XCircleIcon,
} from '@heroicons/react/24/outline';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { submissionApi } from '../api';
import LoadingSpinner from '../components/LoadingSpinner';
import StatusBadge from '../components/StatusBadge';
import type { SubmissionStatus } from '../types';

export default function SubmissionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: submission, isLoading } = useQuery({
    queryKey: ['submission', id],
    queryFn: () => submissionApi.get(Number(id)),
  });

  const runMutation = useMutation({
    mutationFn: (id: number) => submissionApi.run(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['submission', id] });
      toast.success('Submission started');
    },
    onError: () => {
      toast.error('Failed to start submission');
    },
  });

  const retryMutation = useMutation({
    mutationFn: (id: number) => submissionApi.retry(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['submission', id] });
      toast.success('Retry started');
    },
    onError: () => {
      toast.error('Failed to retry submission');
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ status, listingUrl }: { status: SubmissionStatus; listingUrl?: string }) =>
      submissionApi.updateStatus(Number(id), status, listingUrl),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['submission', id] });
      toast.success('Status updated');
    },
    onError: () => {
      toast.error('Failed to update status');
    },
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!submission) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Submission not found</p>
        <Link to="/submissions" className="text-primary-600 hover:underline mt-2 block">
          Back to Submissions
        </Link>
      </div>
    );
  }

  const canRun = submission.status === 'pending';
  const canRetry =
    (submission.status === 'failed' || submission.status === 'rejected') &&
    submission.attempt_count < submission.max_attempts;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/submissions')}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeftIcon className="h-5 w-5 text-gray-500" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Submission Details
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              ID: {submission.id}
            </p>
          </div>
        </div>
        <div className="flex space-x-3">
          {canRun && (
            <button
              onClick={() => runMutation.mutate(submission.id)}
              className="btn-primary"
              disabled={runMutation.isPending}
            >
              <PlayIcon className="h-5 w-5 mr-2" />
              Run Now
            </button>
          )}
          {canRetry && (
            <button
              onClick={() => retryMutation.mutate(submission.id)}
              className="btn-secondary"
              disabled={retryMutation.isPending}
            >
              <ArrowPathIcon className="h-5 w-5 mr-2" />
              Retry
            </button>
          )}
        </div>
      </div>

      {/* Status and Info */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Product & Directory */}
          <div className="card">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Submission Information
            </h2>
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Product</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {submission.saas_product.name}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Directory</dt>
                <dd className="mt-1">
                  <a
                    href={submission.directory.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
                  >
                    {submission.directory.name}
                    <ArrowTopRightOnSquareIcon className="h-4 w-4 ml-1" />
                  </a>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1">
                  <StatusBadge status={submission.status} />
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Attempts</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {submission.attempt_count} / {submission.max_attempts}
                </dd>
              </div>
              {submission.listing_url && (
                <div className="sm:col-span-2">
                  <dt className="text-sm font-medium text-gray-500">Listing URL</dt>
                  <dd className="mt-1">
                    <a
                      href={submission.listing_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
                    >
                      {submission.listing_url}
                      <ArrowTopRightOnSquareIcon className="h-4 w-4 ml-1" />
                    </a>
                  </dd>
                </div>
              )}
              {submission.error_message && (
                <div className="sm:col-span-2">
                  <dt className="text-sm font-medium text-gray-500">Error</dt>
                  <dd className="mt-1 text-sm text-red-600 bg-red-50 p-2 rounded">
                    {submission.error_message}
                  </dd>
                </div>
              )}
            </dl>
          </div>

          {/* Detected Fields */}
          {submission.detected_fields && (
            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Detected Form Fields
              </h2>
              <pre className="text-xs bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">
                {JSON.stringify(submission.detected_fields, null, 2)}
              </pre>
            </div>
          )}

          {/* Filled Fields */}
          {submission.filled_fields && (
            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Filled Fields
              </h2>
              <pre className="text-xs bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">
                {JSON.stringify(submission.filled_fields, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Timeline */}
          <div className="card">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Timeline</h2>
            <ul className="space-y-4">
              <li className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <CheckCircleIcon className="h-4 w-4 text-blue-600" />
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Created</p>
                  <p className="text-xs text-gray-500">
                    {format(new Date(submission.created_at), 'MMM d, yyyy h:mm a')}
                  </p>
                </div>
              </li>
              {submission.submitted_at && (
                <li className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                      <CheckCircleIcon className="h-4 w-4 text-green-600" />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Submitted</p>
                    <p className="text-xs text-gray-500">
                      {format(new Date(submission.submitted_at), 'MMM d, yyyy h:mm a')}
                    </p>
                  </div>
                </li>
              )}
              {submission.approved_at && (
                <li className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                      <CheckCircleIcon className="h-4 w-4 text-green-600" />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Approved</p>
                    <p className="text-xs text-gray-500">
                      {format(new Date(submission.approved_at), 'MMM d, yyyy h:mm a')}
                    </p>
                  </div>
                </li>
              )}
              {submission.status === 'failed' && (
                <li className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center">
                      <XCircleIcon className="h-4 w-4 text-red-600" />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Failed</p>
                    <p className="text-xs text-gray-500">
                      {format(new Date(submission.updated_at), 'MMM d, yyyy h:mm a')}
                    </p>
                  </div>
                </li>
              )}
            </ul>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Manual Status Update
            </h2>
            <div className="space-y-2">
              <button
                onClick={() =>
                  updateStatusMutation.mutate({ status: 'approved' })
                }
                className="w-full btn-success text-sm"
                disabled={updateStatusMutation.isPending}
              >
                Mark as Approved
              </button>
              <button
                onClick={() =>
                  updateStatusMutation.mutate({ status: 'rejected' })
                }
                className="w-full btn-danger text-sm"
                disabled={updateStatusMutation.isPending}
              >
                Mark as Rejected
              </button>
            </div>
          </div>

          {/* Screenshot */}
          {submission.screenshot_path && (
            <div className="card">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Screenshot
              </h2>
              <img
                src={`/uploads/${submission.screenshot_path}`}
                alt="Submission screenshot"
                className="w-full rounded-lg border border-gray-200"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
