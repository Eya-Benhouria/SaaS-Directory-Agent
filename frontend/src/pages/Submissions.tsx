import {
    ArrowPathIcon,
    EyeIcon,
    PlayIcon,
    PlusIcon,
    TrashIcon
} from '@heroicons/react/24/outline';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { Link } from 'react-router-dom';
import { directoryApi, productApi, submissionApi } from '../api';
import EmptyState from '../components/EmptyState';
import LoadingSpinner from '../components/LoadingSpinner';
import Modal from '../components/Modal';
import StatusBadge from '../components/StatusBadge';
import type { SubmissionStatus, SubmissionWithDetails } from '../types';

export default function Submissions() {
  const queryClient = useQueryClient();
  const [deleteModal, setDeleteModal] = useState<SubmissionWithDetails | null>(null);
  const [createModal, setCreateModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState<SubmissionStatus | ''>('');
  const [productFilter, setProductFilter] = useState<number | ''>('');

  // Form state for creating submissions
  const [selectedProduct, setSelectedProduct] = useState<number | ''>('');
  const [selectedDirectories, setSelectedDirectories] = useState<number[]>([]);

  const { data: submissions, isLoading } = useQuery({
    queryKey: ['submissions', statusFilter, productFilter],
    queryFn: () =>
      submissionApi.list(
        productFilter || undefined,
        undefined,
        statusFilter || undefined
      ),
  });

  const { data: products } = useQuery({
    queryKey: ['products'],
    queryFn: productApi.list,
  });

  const { data: directories } = useQuery({
    queryKey: ['active-directories'],
    queryFn: directoryApi.getActive,
  });

  const runMutation = useMutation({
    mutationFn: (id: number) => submissionApi.run(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
      toast.success('Submission started');
    },
    onError: () => {
      toast.error('Failed to start submission');
    },
  });

  const retryMutation = useMutation({
    mutationFn: (id: number) => submissionApi.retry(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
      toast.success('Retry started');
    },
    onError: () => {
      toast.error('Failed to retry submission');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => submissionApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
      toast.success('Submission deleted');
      setDeleteModal(null);
    },
    onError: () => {
      toast.error('Failed to delete submission');
    },
  });

  const createMutation = useMutation({
    mutationFn: ({ productId, directoryIds }: { productId: number; directoryIds: number[] }) =>
      submissionApi.bulkCreate(productId, directoryIds),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
      toast.success(`Created ${data.length} submissions`);
      setCreateModal(false);
      setSelectedProduct('');
      setSelectedDirectories([]);
    },
    onError: () => {
      toast.error('Failed to create submissions');
    },
  });

  const runBatchMutation = useMutation({
    mutationFn: (limit: number) => submissionApi.runBatch(limit),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
      toast.success(`Started ${data.count} submissions`);
    },
    onError: () => {
      toast.error('Failed to run batch');
    },
  });

  const handleCreateSubmissions = () => {
    if (!selectedProduct || selectedDirectories.length === 0) {
      toast.error('Please select a product and at least one directory');
      return;
    }
    createMutation.mutate({
      productId: selectedProduct as number,
      directoryIds: selectedDirectories,
    });
  };

  const toggleDirectory = (id: number) => {
    setSelectedDirectories((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    );
  };

  const selectAllDirectories = () => {
    if (directories) {
      setSelectedDirectories(directories.map((d) => d.id));
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Submissions</h1>
          <p className="mt-1 text-sm text-gray-500">
            Track and manage directory submissions
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => runBatchMutation.mutate(5)}
            className="btn-secondary"
            disabled={runBatchMutation.isPending}
          >
            <PlayIcon className="h-5 w-5 mr-2" />
            Run Batch (5)
          </button>
          <button onClick={() => setCreateModal(true)} className="btn-primary">
            <PlusIcon className="h-5 w-5 mr-2" />
            New Submissions
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label htmlFor="product" className="label">
              Product
            </label>
            <select
              id="product"
              value={productFilter}
              onChange={(e) =>
                setProductFilter(e.target.value ? Number(e.target.value) : '')
              }
              className="input w-48"
            >
              <option value="">All Products</option>
              {products?.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="status" className="label">
              Status
            </label>
            <select
              id="status"
              value={statusFilter}
              onChange={(e) =>
                setStatusFilter(e.target.value as SubmissionStatus | '')
              }
              className="input w-40"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="submitted">Submitted</option>
              <option value="approved">Approved</option>
              <option value="failed">Failed</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>
      </div>

      {/* Submissions List */}
      {submissions && submissions.length > 0 ? (
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Directory
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Attempts
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Updated
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {submissions.map((submission) => (
                <tr key={submission.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-medium text-gray-900">
                      {submission.saas_product.name}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <span className="text-sm text-gray-900">
                        {submission.directory.name}
                      </span>
                      {submission.listing_url && (
                        <a
                          href={submission.listing_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block text-xs text-primary-600 hover:underline"
                        >
                          View Listing
                        </a>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <StatusBadge status={submission.status} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-500">
                      {submission.attempt_count} / {submission.max_attempts}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-500">
                      {format(new Date(submission.updated_at), 'MMM d, h:mm a')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-2">
                      {submission.status === 'pending' && (
                        <button
                          onClick={() => runMutation.mutate(submission.id)}
                          className="text-green-600 hover:text-green-900 p-1"
                          title="Run"
                        >
                          <PlayIcon className="h-5 w-5" />
                        </button>
                      )}
                      {(submission.status === 'failed' ||
                        submission.status === 'rejected') &&
                        submission.attempt_count < submission.max_attempts && (
                          <button
                            onClick={() => retryMutation.mutate(submission.id)}
                            className="text-yellow-600 hover:text-yellow-900 p-1"
                            title="Retry"
                          >
                            <ArrowPathIcon className="h-5 w-5" />
                          </button>
                        )}
                      <Link
                        to={`/submissions/${submission.id}`}
                        className="text-primary-600 hover:text-primary-900 p-1"
                        title="View Details"
                      >
                        <EyeIcon className="h-5 w-5" />
                      </Link>
                      <button
                        onClick={() => setDeleteModal(submission)}
                        className="text-red-600 hover:text-red-900 p-1"
                        title="Delete"
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="card">
          <EmptyState
            title="No submissions yet"
            description="Create submissions to start the automated directory listing process"
            action={
              <button onClick={() => setCreateModal(true)} className="btn-primary">
                <PlusIcon className="h-5 w-5 mr-2" />
                New Submissions
              </button>
            }
          />
        </div>
      )}

      {/* Delete Modal */}
      <Modal
        isOpen={!!deleteModal}
        onClose={() => setDeleteModal(null)}
        title="Delete Submission"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            Are you sure you want to delete this submission? This action cannot
            be undone.
          </p>
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setDeleteModal(null)}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={() =>
                deleteModal && deleteMutation.mutate(deleteModal.id)
              }
              className="btn-danger"
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </div>
      </Modal>

      {/* Create Submissions Modal */}
      <Modal
        isOpen={createModal}
        onClose={() => setCreateModal(false)}
        title="Create New Submissions"
        size="lg"
      >
        <div className="space-y-6">
          {/* Product Selection */}
          <div>
            <label htmlFor="select-product" className="label">
              Select Product *
            </label>
            <select
              id="select-product"
              value={selectedProduct}
              onChange={(e) =>
                setSelectedProduct(e.target.value ? Number(e.target.value) : '')
              }
              className="input"
            >
              <option value="">Select a product</option>
              {products?.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </select>
          </div>

          {/* Directory Selection */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="label mb-0">
                Select Directories ({selectedDirectories.length} selected)
              </label>
              <button
                type="button"
                onClick={selectAllDirectories}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                Select All
              </button>
            </div>
            <div className="max-h-64 overflow-y-auto border border-gray-200 rounded-lg divide-y">
              {directories?.map((directory) => (
                <label
                  key={directory.id}
                  className="flex items-center p-3 hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedDirectories.includes(directory.id)}
                    onChange={() => toggleDirectory(directory.id)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-3 text-sm text-gray-900">
                    {directory.name}
                  </span>
                  {directory.domain_authority && (
                    <span className="ml-auto text-xs text-gray-500">
                      DA: {directory.domain_authority}
                    </span>
                  )}
                </label>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setCreateModal(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={handleCreateSubmissions}
              className="btn-primary"
              disabled={createMutation.isPending}
            >
              {createMutation.isPending
                ? 'Creating...'
                : `Create ${selectedDirectories.length} Submissions`}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
