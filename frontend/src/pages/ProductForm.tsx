import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate, useParams } from 'react-router-dom';
import { productApi } from '../api';
import LoadingSpinner from '../components/LoadingSpinner';
import type { SaaSProductCreate } from '../types';

const initialFormData: SaaSProductCreate = {
  name: '',
  website_url: '',
  tagline: '',
  short_description: '',
  long_description: '',
  category: '',
  subcategory: '',
  tags: [],
  contact_email: '',
  contact_name: '',
  twitter_url: '',
  linkedin_url: '',
  github_url: '',
  pricing_model: '',
  pricing_details: '',
};

export default function ProductForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const queryClient = useQueryClient();
  const isEditing = !!id;

  const [formData, setFormData] = useState<SaaSProductCreate>(initialFormData);
  const [tagsInput, setTagsInput] = useState('');
  const [logoFile, setLogoFile] = useState<File | null>(null);

  const { data: product, isLoading: productLoading } = useQuery({
    queryKey: ['product', id],
    queryFn: () => productApi.get(Number(id)),
    enabled: isEditing,
  });

  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name,
        website_url: product.website_url,
        tagline: product.tagline || '',
        short_description: product.short_description || '',
        long_description: product.long_description || '',
        category: product.category || '',
        subcategory: product.subcategory || '',
        tags: product.tags || [],
        contact_email: product.contact_email,
        contact_name: product.contact_name || '',
        twitter_url: product.twitter_url || '',
        linkedin_url: product.linkedin_url || '',
        github_url: product.github_url || '',
        pricing_model: product.pricing_model || '',
        pricing_details: product.pricing_details || '',
      });
      setTagsInput((product.tags || []).join(', '));
    }
  }, [product]);

  const createMutation = useMutation({
    mutationFn: async (data: SaaSProductCreate) => {
      const product = await productApi.create(data);
      if (logoFile) {
        await productApi.uploadLogo(product.id, logoFile);
      }
      return product;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      toast.success('Product created successfully');
      navigate('/products');
    },
    onError: () => {
      toast.error('Failed to create product');
    },
  });

  const updateMutation = useMutation({
    mutationFn: async (data: SaaSProductCreate) => {
      const product = await productApi.update(Number(id), data);
      if (logoFile) {
        await productApi.uploadLogo(product.id, logoFile);
      }
      return product;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['product', id] });
      toast.success('Product updated successfully');
      navigate('/products');
    },
    onError: () => {
      toast.error('Failed to update product');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const data = {
      ...formData,
      tags: tagsInput.split(',').map(t => t.trim()).filter(Boolean),
    };

    if (isEditing) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  if (isEditing && productLoading) {
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
          {isEditing ? 'Edit Product' : 'Add New Product'}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {isEditing
            ? 'Update your SaaS product information'
            : 'Add a new SaaS product to submit to directories'}
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
                Product Name *
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="input"
                placeholder="e.g., Genie Ops"
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="website_url" className="label">
                Website URL *
              </label>
              <input
                type="url"
                id="website_url"
                name="website_url"
                value={formData.website_url}
                onChange={handleChange}
                required
                className="input"
                placeholder="https://www.genie-ops.com"
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="tagline" className="label">
                Tagline
              </label>
              <input
                type="text"
                id="tagline"
                name="tagline"
                value={formData.tagline}
                onChange={handleChange}
                className="input"
                placeholder="A short catchy phrase"
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="short_description" className="label">
                Short Description
              </label>
              <textarea
                id="short_description"
                name="short_description"
                value={formData.short_description}
                onChange={handleChange}
                rows={2}
                className="input"
                placeholder="Brief description (1-2 sentences)"
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="long_description" className="label">
                Long Description
              </label>
              <textarea
                id="long_description"
                name="long_description"
                value={formData.long_description}
                onChange={handleChange}
                rows={4}
                className="input"
                placeholder="Detailed description of your product"
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
                <option value="AI">AI & Machine Learning</option>
                <option value="Productivity">Productivity</option>
                <option value="Marketing">Marketing</option>
                <option value="Sales">Sales</option>
                <option value="Developer Tools">Developer Tools</option>
                <option value="Design">Design</option>
                <option value="Analytics">Analytics</option>
                <option value="Communication">Communication</option>
                <option value="Finance">Finance</option>
                <option value="HR">HR & Recruiting</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label htmlFor="pricing_model" className="label">
                Pricing Model
              </label>
              <select
                id="pricing_model"
                name="pricing_model"
                value={formData.pricing_model}
                onChange={handleChange}
                className="input"
              >
                <option value="">Select pricing</option>
                <option value="free">Free</option>
                <option value="freemium">Freemium</option>
                <option value="paid">Paid</option>
                <option value="subscription">Subscription</option>
                <option value="one-time">One-time Purchase</option>
              </select>
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="tags" className="label">
                Tags (comma-separated)
              </label>
              <input
                type="text"
                id="tags"
                value={tagsInput}
                onChange={(e) => setTagsInput(e.target.value)}
                className="input"
                placeholder="e.g., AI, Automation, SaaS"
              />
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="logo" className="label">
                Logo
              </label>
              <input
                type="file"
                id="logo"
                accept="image/*"
                onChange={(e) => setLogoFile(e.target.files?.[0] || null)}
                className="input"
              />
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Contact Information
          </h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label htmlFor="contact_email" className="label">
                Contact Email *
              </label>
              <input
                type="email"
                id="contact_email"
                name="contact_email"
                value={formData.contact_email}
                onChange={handleChange}
                required
                className="input"
                placeholder="contact@genie-ops.com"
              />
            </div>

            <div>
              <label htmlFor="contact_name" className="label">
                Contact Name
              </label>
              <input
                type="text"
                id="contact_name"
                name="contact_name"
                value={formData.contact_name}
                onChange={handleChange}
                className="input"
                placeholder="John Doe"
              />
            </div>
          </div>
        </div>

        {/* Social Links */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Social Links
          </h2>
          <div className="grid grid-cols-1 gap-6">
            <div>
              <label htmlFor="twitter_url" className="label">
                Twitter URL
              </label>
              <input
                type="url"
                id="twitter_url"
                name="twitter_url"
                value={formData.twitter_url}
                onChange={handleChange}
                className="input"
                placeholder="https://twitter.com/genieops"
              />
            </div>

            <div>
              <label htmlFor="linkedin_url" className="label">
                LinkedIn URL
              </label>
              <input
                type="url"
                id="linkedin_url"
                name="linkedin_url"
                value={formData.linkedin_url}
                onChange={handleChange}
                className="input"
                placeholder="https://linkedin.com/company/genieops"
              />
            </div>

            <div>
              <label htmlFor="github_url" className="label">
                GitHub URL
              </label>
              <input
                type="url"
                id="github_url"
                name="github_url"
                value={formData.github_url}
                onChange={handleChange}
                className="input"
                placeholder="https://github.com/genieops"
              />
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/products')}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary"
            disabled={isPending}
          >
            {isPending
              ? 'Saving...'
              : isEditing
              ? 'Update Product'
              : 'Create Product'}
          </button>
        </div>
      </form>
    </div>
  );
}
