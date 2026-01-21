import {
    GlobeAltIcon,
    PencilIcon,
    PlusIcon,
    TrashIcon,
} from '@heroicons/react/24/outline';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { Link } from 'react-router-dom';
import { productApi } from '../api';
import EmptyState from '../components/EmptyState';
import LoadingSpinner from '../components/LoadingSpinner';
import Modal from '../components/Modal';
import type { SaaSProduct } from '../types';

export default function Products() {
  const queryClient = useQueryClient();
  const [deleteModal, setDeleteModal] = useState<SaaSProduct | null>(null);

  const { data: products, isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: productApi.list,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => productApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      toast.success('Product deleted successfully');
      setDeleteModal(null);
    },
    onError: () => {
      toast.error('Failed to delete product');
    },
  });

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
          <h1 className="text-2xl font-bold text-gray-900">SaaS Products</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your SaaS products to submit to directories
          </p>
        </div>
        <Link to="/products/new" className="btn-primary">
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Product
        </Link>
      </div>

      {/* Products List */}
      {products && products.length > 0 ? (
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact
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
              {products.map((product) => (
                <tr key={product.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        {product.logo_path ? (
                          <img
                            className="h-10 w-10 rounded-lg object-cover"
                            src={`/uploads/${product.logo_path}`}
                            alt={product.name}
                          />
                        ) : (
                          <div className="h-10 w-10 rounded-lg bg-primary-100 flex items-center justify-center">
                            <span className="text-primary-700 font-semibold text-sm">
                              {product.name.substring(0, 2).toUpperCase()}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {product.name}
                        </div>
                        <a
                          href={product.website_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
                        >
                          <GlobeAltIcon className="h-3 w-3 mr-1" />
                          {new URL(product.website_url).hostname}
                        </a>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900">
                      {product.category || '-'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-500">
                      {product.contact_email}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        product.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {product.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-2">
                      <Link
                        to={`/products/${product.id}/edit`}
                        className="text-primary-600 hover:text-primary-900 p-1"
                      >
                        <PencilIcon className="h-5 w-5" />
                      </Link>
                      <button
                        onClick={() => setDeleteModal(product)}
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
            title="No products yet"
            description="Get started by adding your first SaaS product"
            action={
              <Link to="/products/new" className="btn-primary">
                <PlusIcon className="h-5 w-5 mr-2" />
                Add Product
              </Link>
            }
          />
        </div>
      )}

      {/* Delete Modal */}
      <Modal
        isOpen={!!deleteModal}
        onClose={() => setDeleteModal(null)}
        title="Delete Product"
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
