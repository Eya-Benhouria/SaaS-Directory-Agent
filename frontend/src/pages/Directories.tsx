import {
    ArrowTopRightOnSquareIcon,
    MagnifyingGlassIcon,
    PencilIcon,
    PlusIcon,
    TrashIcon,
} from '@heroicons/react/24/outline';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { Link } from 'react-router-dom';
import { directoryApi } from '../api';
import EmptyState from '../components/EmptyState';
import LoadingSpinner from '../components/LoadingSpinner';
import Modal from '../components/Modal';
import type { Directory, DirectoryStatus } from '../types';

export default function Directories() {
  const queryClient = useQueryClient();
  const [deleteModal, setDeleteModal] = useState<Directory | null>(null);
  const [statusFilter, setStatusFilter] = useState<DirectoryStatus | ''>('');
  const [categoryFilter, setCategoryFilter] = useState('');

  const { data: directories, isLoading } = useQuery({
    queryKey: ['directories', statusFilter, categoryFilter],
    queryFn: () => directoryApi.list(statusFilter || undefined, categoryFilter || undefined),
  });

  const { data: categories } = useQuery({
    queryKey: ['directory-categories'],
    queryFn: directoryApi.getCategories,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => directoryApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['directories'] });
      toast.success('Directory deleted successfully');
      setDeleteModal(null);
    },
    onError: () => {
      toast.error('Failed to delete directory');
    },
  });

  const analyzeMutation = useMutation({
    mutationFn: (id: number) => directoryApi.analyze(id),
    onSuccess: () => {
      toast.success('Analysis started');
    },
    onError: () => {
      toast.error('Failed to start analysis');
    },
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const getStatusBadge = (status: DirectoryStatus) => {
    const styles = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      blocked: 'bg-red-100 text-red-800',
      needs_update: 'bg-yellow-100 text-yellow-800',
    };

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status]}`}
      >
        {status.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Directories</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage directory websites for submissions
          </p>
        </div>
        <Link to="/directories/new" className="btn-primary">
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Directory
        </Link>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-wrap gap-4">
          <div>
            <label htmlFor="status" className="label">
              Status
            </label>
            <select
              id="status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as DirectoryStatus | '')}
              className="input w-40"
            >
              <option value="">All</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="blocked">Blocked</option>
              <option value="needs_update">Needs Update</option>
            </select>
          </div>
          <div>
            <label htmlFor="category" className="label">
              Category
            </label>
            <select
              id="category"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="input w-48"
            >
              <option value="">All Categories</option>
              {categories?.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Directories List */}
      {directories && directories.length > 0 ? (
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Directory
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  DA
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Success Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {directories.map((directory) => (
                <tr key={directory.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {directory.name}
                      </div>
                      <a
                        href={directory.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
                      >
                        {new URL(directory.url).hostname}
                        <ArrowTopRightOnSquareIcon className="h-3 w-3 ml-1" />
                      </a>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-500">
                      {directory.category || '-'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900">
                      {directory.domain_authority || '-'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${directory.success_rate}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-900">
                        {directory.success_rate}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(directory.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => analyzeMutation.mutate(directory.id)}
                        className="text-gray-600 hover:text-gray-900 p-1"
                        title="Analyze form"
                      >
                        <MagnifyingGlassIcon className="h-5 w-5" />
                      </button>
                      <Link
                        to={`/directories/${directory.id}/edit`}
                        className="text-primary-600 hover:text-primary-900 p-1"
                      >
                        <PencilIcon className="h-5 w-5" />
                      </Link>
                      <button
                        onClick={() => setDeleteModal(directory)}
                        className="text-red-600 hover:text-red-900 p-1"
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
            title="No directories yet"
            description="Add directories to submit your SaaS products"
            action={
              <Link to="/directories/new" className="btn-primary">
                <PlusIcon className="h-5 w-5 mr-2" />
                Add Directory
              </Link>
            }
          />
        </div>
      )}

      {/* Delete Modal */}
      <Modal
        isOpen={!!deleteModal}
        onClose={() => setDeleteModal(null)}
        title="Delete Directory"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            Are you sure you want to delete{' '}
            <span className="font-semibold text-gray-900">
              {deleteModal?.name}
            </span>
            ? This action cannot be undone.
          </p>
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setDeleteModal(null)}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={() => deleteModal && deleteMutation.mutate(deleteModal.id)}
              className="btn-danger"
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
