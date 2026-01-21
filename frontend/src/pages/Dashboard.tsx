import {
    ArrowTrendingUpIcon,
    BeakerIcon,
    CheckCircleIcon,
    ClockIcon,
    CubeIcon,
    GlobeAltIcon,
    PaperAirplaneIcon,
    XCircleIcon,
} from '@heroicons/react/24/outline';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Link } from 'react-router-dom';
import {
    CartesianGrid,
    Cell,
    Line,
    LineChart,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts';
import { dashboardApi, submissionApi } from '../api';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: dashboardApi.getStats,
  });

  const { data: trends, isLoading: trendsLoading } = useQuery({
    queryKey: ['dashboard-trends'],
    queryFn: () => dashboardApi.getTrends(7),
  });

  const { data: activity } = useQuery({
    queryKey: ['recent-activity'],
    queryFn: () => dashboardApi.getRecentActivity(10),
  });

  const { data: systemStatus } = useQuery({
    queryKey: ['system-status'],
    queryFn: dashboardApi.getSystemStatus,
  });

  if (statsLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const pieData = stats ? [
    { name: 'Pending', value: stats.pending_submissions, color: '#fbbf24' },
    { name: 'Submitted', value: stats.submitted_submissions, color: '#3b82f6' },
    { name: 'Approved', value: stats.approved_submissions, color: '#22c55e' },
    { name: 'Failed', value: stats.failed_submissions, color: '#ef4444' },
  ].filter(item => item.value > 0) : [];

  return (
    <div className="space-y-6">
      {/* Demo Mode Banner */}
      {systemStatus?.demo_mode && (
        <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded-r-lg">
          <div className="flex items-center">
            <BeakerIcon className="h-6 w-6 text-amber-600 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-amber-800">Demo Mode Active</h3>
              <p className="text-sm text-amber-700 mt-1">
                Submissions are simulated for demonstration purposes. Set <code className="bg-amber-100 px-1 rounded">DEMO_MODE=false</code> and add your LLM API key for production use.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            Overview of your SaaS directory submissions
          </p>
        </div>
        <div className="flex space-x-3">
          <Link to="/products/new" className="btn-secondary">
            Add Product
          </Link>
          <button
            onClick={() => submissionApi.runBatch(5)}
            className="btn-primary"
          >
            Run Submissions
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Products"
          value={stats?.total_products || 0}
          icon={<CubeIcon className="h-6 w-6 text-blue-600" />}
          bgColor="bg-blue-50"
        />
        <StatCard
          title="Total Directories"
          value={stats?.total_directories || 0}
          icon={<GlobeAltIcon className="h-6 w-6 text-purple-600" />}
          bgColor="bg-purple-50"
        />
        <StatCard
          title="Total Submissions"
          value={stats?.total_submissions || 0}
          icon={<PaperAirplaneIcon className="h-6 w-6 text-green-600" />}
          bgColor="bg-green-50"
        />
        <StatCard
          title="Success Rate"
          value={`${stats?.success_rate || 0}%`}
          icon={<ArrowTrendingUpIcon className="h-6 w-6 text-yellow-600" />}
          bgColor="bg-yellow-50"
        />
      </div>

      {/* Submission Status Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5">
        <StatusCard
          label="Pending"
          value={stats?.pending_submissions || 0}
          icon={<ClockIcon className="h-5 w-5" />}
          color="yellow"
        />
        <StatusCard
          label="In Progress"
          value={stats?.in_progress_submissions || 0}
          icon={<PaperAirplaneIcon className="h-5 w-5" />}
          color="purple"
        />
        <StatusCard
          label="Submitted"
          value={stats?.submitted_submissions || 0}
          icon={<CheckCircleIcon className="h-5 w-5" />}
          color="blue"
        />
        <StatusCard
          label="Approved"
          value={stats?.approved_submissions || 0}
          icon={<CheckCircleIcon className="h-5 w-5" />}
          color="green"
        />
        <StatusCard
          label="Failed"
          value={stats?.failed_submissions || 0}
          icon={<XCircleIcon className="h-5 w-5" />}
          color="red"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Trends Chart */}
        <div className="lg:col-span-2 card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Submission Trends (Last 7 Days)
          </h3>
          {trendsLoading ? (
            <LoadingSpinner />
          ) : trends && trends.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(date) => format(new Date(date), 'MMM d')}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(date) => format(new Date(date), 'MMM d, yyyy')}
                />
                <Line 
                  type="monotone" 
                  dataKey="submitted" 
                  stroke="#3b82f6" 
                  name="Submitted"
                  strokeWidth={2}
                />
                <Line 
                  type="monotone" 
                  dataKey="approved" 
                  stroke="#22c55e" 
                  name="Approved"
                  strokeWidth={2}
                />
                <Line 
                  type="monotone" 
                  dataKey="failed" 
                  stroke="#ef4444" 
                  name="Failed"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              No data available
            </div>
          )}
        </div>

        {/* Pie Chart */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Status Distribution
          </h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              No submissions yet
            </div>
          )}
          <div className="flex flex-wrap justify-center gap-4 mt-4">
            {pieData.map((item) => (
              <div key={item.name} className="flex items-center space-x-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: item.color }} 
                />
                <span className="text-sm text-gray-600">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        {activity && activity.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {activity.map((log) => (
              <li key={log.id} className="py-3 flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-900">{log.message}</p>
                  <p className="text-xs text-gray-500">{log.action}</p>
                </div>
                <span className="text-xs text-gray-400">
                  {format(new Date(log.created_at), 'MMM d, h:mm a')}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500 text-center py-8">No recent activity</p>
        )}
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({ 
  title, 
  value, 
  icon, 
  bgColor 
}: { 
  title: string; 
  value: number | string; 
  icon: React.ReactNode; 
  bgColor: string;
}) {
  return (
    <div className="card flex items-center">
      <div className={`${bgColor} rounded-lg p-3 mr-4`}>
        {icon}
      </div>
      <div>
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <p className="text-2xl font-semibold text-gray-900">{value}</p>
      </div>
    </div>
  );
}

// Status Card Component
function StatusCard({ 
  label, 
  value, 
  icon, 
  color 
}: { 
  label: string; 
  value: number; 
  icon: React.ReactNode; 
  color: 'yellow' | 'purple' | 'blue' | 'green' | 'red';
}) {
  const colorClasses = {
    yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    red: 'bg-red-50 text-red-600 border-red-200',
  };

  return (
    <div className={`rounded-lg border p-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{label}</span>
        {icon}
      </div>
      <p className="mt-2 text-2xl font-bold">{value}</p>
    </div>
  );
}
