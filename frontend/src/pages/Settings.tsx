import {
    BellIcon,
    CheckCircleIcon,
    Cog6ToothIcon,
    ExclamationTriangleIcon,
    GlobeAltIcon,
    KeyIcon,
    ServerIcon,
} from '@heroicons/react/24/outline';
import { useState } from 'react';

interface SettingsSection {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
}

const sections: SettingsSection[] = [
  { id: 'general', name: 'General', icon: Cog6ToothIcon },
  { id: 'api', name: 'API Configuration', icon: KeyIcon },
  { id: 'browser', name: 'Browser Automation', icon: GlobeAltIcon },
  { id: 'notifications', name: 'Notifications', icon: BellIcon },
  { id: 'database', name: 'Database', icon: ServerIcon },
];

export default function Settings() {
  const [activeSection, setActiveSection] = useState('general');
  const [settings, setSettings] = useState({
    // General
    maxConcurrentSubmissions: 3,
    defaultRetryCount: 3,
    submissionDelayMs: 5000,
    
    // API
    llmProvider: 'openai',
    llmModel: 'gpt-4o',
    openaiApiKey: '',
    anthropicApiKey: '',
    
    // Browser
    browserHeadless: true,
    browserTimeout: 30000,
    screenshotOnSubmit: true,
    
    // Notifications
    emailNotifications: false,
    notifyOnSuccess: true,
    notifyOnFailure: true,
    notificationEmail: '',
    
    // Database
    autoBackup: false,
    backupFrequency: 'daily',
  });
  
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (key: string, value: string | number | boolean) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setSaved(false);
  };

  const handleSave = async () => {
    try {
      // In a real app, this would save to the backend
      // await api.saveSettings(settings);
      setSaved(true);
      setError(null);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setError('Failed to save settings');
    }
  };

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Submission Settings</h3>
        <p className="mt-1 text-sm text-gray-500">
          Configure how submissions are processed.
        </p>
      </div>
      
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Max Concurrent Submissions
          </label>
          <input
            type="number"
            min="1"
            max="10"
            value={settings.maxConcurrentSubmissions}
            onChange={(e) => handleChange('maxConcurrentSubmissions', parseInt(e.target.value))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <p className="mt-1 text-xs text-gray-500">
            Number of submissions to process simultaneously
          </p>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Default Retry Count
          </label>
          <input
            type="number"
            min="0"
            max="10"
            value={settings.defaultRetryCount}
            onChange={(e) => handleChange('defaultRetryCount', parseInt(e.target.value))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <p className="mt-1 text-xs text-gray-500">
            Number of retries for failed submissions
          </p>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Submission Delay (ms)
          </label>
          <input
            type="number"
            min="1000"
            max="60000"
            step="1000"
            value={settings.submissionDelayMs}
            onChange={(e) => handleChange('submissionDelayMs', parseInt(e.target.value))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <p className="mt-1 text-xs text-gray-500">
            Delay between submissions to avoid rate limiting
          </p>
        </div>
      </div>
    </div>
  );

  const renderApiSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">LLM Configuration</h3>
        <p className="mt-1 text-sm text-gray-500">
          Configure the AI provider for form detection.
        </p>
      </div>
      
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            LLM Provider
          </label>
          <select
            value={settings.llmProvider}
            onChange={(e) => handleChange('llmProvider', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Model
          </label>
          <select
            value={settings.llmModel}
            onChange={(e) => handleChange('llmModel', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            {settings.llmProvider === 'openai' ? (
              <>
                <option value="gpt-4o">GPT-4o</option>
                <option value="gpt-4-vision-preview">GPT-4 Vision</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
              </>
            ) : (
              <>
                <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
              </>
            )}
          </select>
        </div>
        
        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-gray-700">
            OpenAI API Key
          </label>
          <input
            type="password"
            value={settings.openaiApiKey}
            onChange={(e) => handleChange('openaiApiKey', e.target.value)}
            placeholder="sk-..."
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>
        
        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-gray-700">
            Anthropic API Key
          </label>
          <input
            type="password"
            value={settings.anthropicApiKey}
            onChange={(e) => handleChange('anthropicApiKey', e.target.value)}
            placeholder="sk-ant-..."
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>
      </div>
    </div>
  );

  const renderBrowserSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Browser Automation</h3>
        <p className="mt-1 text-sm text-gray-500">
          Configure Playwright browser settings.
        </p>
      </div>
      
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={settings.browserHeadless}
            onChange={(e) => handleChange('browserHeadless', e.target.checked)}
            className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          <label className="ml-2 block text-sm text-gray-900">
            Run browser in headless mode
          </label>
        </div>
        
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={settings.screenshotOnSubmit}
            onChange={(e) => handleChange('screenshotOnSubmit', e.target.checked)}
            className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          <label className="ml-2 block text-sm text-gray-900">
            Capture screenshot after submission
          </label>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Browser Timeout (ms)
          </label>
          <input
            type="number"
            min="10000"
            max="120000"
            step="5000"
            value={settings.browserTimeout}
            onChange={(e) => handleChange('browserTimeout', parseInt(e.target.value))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <p className="mt-1 text-xs text-gray-500">
            Maximum time to wait for page loads
          </p>
        </div>
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Notifications</h3>
        <p className="mt-1 text-sm text-gray-500">
          Configure email notifications for submissions.
        </p>
      </div>
      
      <div className="space-y-4">
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={settings.emailNotifications}
            onChange={(e) => handleChange('emailNotifications', e.target.checked)}
            className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          <label className="ml-2 block text-sm text-gray-900">
            Enable email notifications
          </label>
        </div>
        
        {settings.emailNotifications && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Notification Email
              </label>
              <input
                type="email"
                value={settings.notificationEmail}
                onChange={(e) => handleChange('notificationEmail', e.target.value)}
                placeholder="your@email.com"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={settings.notifyOnSuccess}
                onChange={(e) => handleChange('notifyOnSuccess', e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label className="ml-2 block text-sm text-gray-900">
                Notify on successful submissions
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={settings.notifyOnFailure}
                onChange={(e) => handleChange('notifyOnFailure', e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label className="ml-2 block text-sm text-gray-900">
                Notify on failed submissions
              </label>
            </div>
          </>
        )}
      </div>
    </div>
  );

  const renderDatabaseSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Database</h3>
        <p className="mt-1 text-sm text-gray-500">
          Database backup and maintenance settings.
        </p>
      </div>
      
      <div className="space-y-4">
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={settings.autoBackup}
            onChange={(e) => handleChange('autoBackup', e.target.checked)}
            className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          <label className="ml-2 block text-sm text-gray-900">
            Enable automatic backups
          </label>
        </div>
        
        {settings.autoBackup && (
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Backup Frequency
            </label>
            <select
              value={settings.backupFrequency}
              onChange={(e) => handleChange('backupFrequency', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option value="hourly">Hourly</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>
        )}
        
        <div className="pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900">Database Status</h4>
          <div className="mt-2 bg-green-50 p-3 rounded-md">
            <div className="flex items-center">
              <CheckCircleIcon className="h-5 w-5 text-green-400" />
              <span className="ml-2 text-sm text-green-700">Connected to PostgreSQL</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderActiveSection = () => {
    switch (activeSection) {
      case 'general':
        return renderGeneralSettings();
      case 'api':
        return renderApiSettings();
      case 'browser':
        return renderBrowserSettings();
      case 'notifications':
        return renderNotificationSettings();
      case 'database':
        return renderDatabaseSettings();
      default:
        return renderGeneralSettings();
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
        <p className="mt-1 text-sm text-gray-500">
          Configure your SaaS Directory Submission Agent
        </p>
      </div>

      <div className="flex gap-6">
        {/* Sidebar Navigation */}
        <nav className="w-64 flex-shrink-0">
          <ul className="space-y-1">
            {sections.map((section) => {
              const Icon = section.icon;
              return (
                <li key={section.id}>
                  <button
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                      activeSection === section.id
                        ? 'bg-indigo-50 text-indigo-600'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <Icon className="mr-3 h-5 w-5" />
                    {section.name}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Settings Content */}
        <div className="flex-1 bg-white shadow rounded-lg p-6">
          {renderActiveSection()}
          
          {/* Save Button */}
          <div className="mt-6 pt-6 border-t border-gray-200 flex items-center justify-between">
            <div>
              {saved && (
                <div className="flex items-center text-green-600">
                  <CheckCircleIcon className="h-5 w-5 mr-2" />
                  <span className="text-sm">Settings saved successfully</span>
                </div>
              )}
              {error && (
                <div className="flex items-center text-red-600">
                  <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
                  <span className="text-sm">{error}</span>
                </div>
              )}
            </div>
            <button
              onClick={handleSave}
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
