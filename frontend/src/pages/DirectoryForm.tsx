import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate, useParams } from 'react-router-dom';
import { directoryApi } from '../api';
import LoadingSpinner from '../components/LoadingSpinner';
import type { DirectoryCreate } from '../types';

const initialFormData: DirectoryCreate = {
  name: '',
  url: '',
  submission_url: '',
  category: '',
  domain_authority: undefined,
  monthly_traffic: undefined,
  requires_account: false,
  requires_approval: true,
  requires_payment: false,
  notes: '',
};

export default function DirectoryForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const queryClient = useQueryClient();
  const isEditing = !!id;

  const [formData, setFormData] = useState<DirectoryCreate>(initialFormData);

  const { data: directory, isLoading: directoryLoading } = useQuery({
    queryKey: ['directory', id],
    queryFn: () => directoryApi.get(Number(id)),
    enabled: isEditing,
  });

  useEffect(() => {
    if (directory) {
      setFormData({
        name: directory.name,
        url: directory.url,
        submission_url: directory.submission_url || '',
        category: directory.category || '',
        domain_authority: directory.domain_authority || undefined,
        monthly_traffic: directory.monthly_traffic || undefined,
        requires_account: directory.requires_account,
        requires_approval: directory.requires_approval,
        requires_payment: directory.requires_payment,
        notes: directory.notes || '',
      });
    }
  }, [directory]);

  const createMutation = useMutation({
    mutationFn: directoryApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['directories'] });
      toast.success('Directory created successfully');
      navigate('/directories');
    },
    onError: () => {
      toast.error('Failed to create directory');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: DirectoryCreate) =>
      directoryApi.update(Number(id), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['directories'] });
      queryClient.invalidateQueries({ queryKey: ['directory', id] });
      toast.success('Directory updated successfully');
      navigate('/directories');
    },
    onError: () => {
      toast.error('Failed to update directory');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (isEditing) {
      updateMutation.mutate(formData);
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
    } else if (type === 'number') {
      setFormData((prev) => ({
        ...prev,
        [name]: value ? parseInt(value, 10) : undefined,
      }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  if (isEditing && directoryLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const isPending = createMutation.isPending || updateMutation.isPending;

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          {isEditing ? 'Edit Directory' : 'Add New Directory'}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {isEditing
            ? 'Update directory information'
            : 'Add a new directory for SaaS submissions'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Basic Information
          </h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label htmlFor="name" className="label">
                Directory Name *
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="input"
                placeholder="e.g., Product Hunt"
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="url" className="label">
                Website URL *
              </label>
              <input
                type="url"
                id="url"
                name="url"
                value={formData.url}
                onChange={handleChange}
                required
                className="input"
                placeholder="https://www.producthunt.com"
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="submission_url" className="label">
                Submission URL
              </label>
              <input
                type="url"
                id="submission_url"
                name="submission_url"
                value={formData.submission_url}
                onChange={handleChange}
                className="input"
                placeholder="Direct link to submission form"
              />
            </div>

            <div>
              <label htmlFor="category" className="label">
                Category
              </label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                className="input"
              >
                <option value="">Select a category</option>
                <option value="General">General</option>
                <option value="Startup">Startup Directories</option>
                <option value="SaaS">SaaS Directories</option>
                <option value="AI">AI/ML Directories</option>
                <option value="Developer">Developer Tools</option>
                <option value="Business">Business Software</option>
                <option value="Marketing">Marketing Tools</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label htmlFor="domain_authority" className="label">
                Domain Authority (0-100)
              </label>
              <input
                type="number"
                id="domain_authority"
                name="domain_authority"
                value={formData.domain_authority || ''}
                onChange={handleChange}
                min="0"
                max="100"
                className="input"
                placeholder="e.g., 85"
              />
            </div>

            <div>
              <label htmlFor="monthly_traffic" className="label">
                Monthly Traffic
              </label>
              <input
                type="number"
                id="monthly_traffic"
                name="monthly_traffic"
                value={formData.monthly_traffic || ''}
                onChange={handleChange}
                min="0"
                className="input"
                placeholder="e.g., 1000000"
              />
            </div>
          </div>
        </div>

        {/* Requirements */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Requirements
          </h2>
          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="requires_account"
                name="requires_account"
                checked={formData.requires_account}
                onChange={handleChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label
                htmlFor="requires_account"
                className="ml-2 block text-sm text-gray-900"
              >
                Requires account registration
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="requires_approval"
                name="requires_approval"
                checked={formData.requires_approval}
                onChange={handleChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label
                htmlFor="requires_approval"
                className="ml-2 block text-sm text-gray-900"
              >
                Requires approval before listing
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="requires_payment"
                name="requires_payment"
                checked={formData.requires_payment}
                onChange={handleChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label
                htmlFor="requires_payment"
                className="ml-2 block text-sm text-gray-900"
              >
                Requires payment for listing
              </label>
            </div>
          </div>
        </div>

        {/* Notes */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Notes</h2>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            rows={3}
            className="input"
            placeholder="Any additional notes about this directory..."
          />
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/directories')}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button type="submit" className="btn-primary" disabled={isPending}>
            {isPending
              ? 'Saving...'
              : isEditing
              ? 'Update Directory'
              : 'Create Directory'}
          </button>
        </div>
      </form>
    </div>
  );
}
