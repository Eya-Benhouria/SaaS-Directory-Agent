import {
    CubeIcon,
    GlobeAltIcon,
    HomeIcon,
    PaperAirplaneIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { NavLink, useLocation } from 'react-router-dom';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Products', href: '/products', icon: CubeIcon },
  { name: 'Directories', href: '/directories', icon: GlobeAltIcon },
  { name: 'Submissions', href: '/submissions', icon: PaperAirplaneIcon },
];

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        {/* Logo */}
        <div className="flex h-16 items-center justify-center border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-lg bg-primary-600 flex items-center justify-center">
              <PaperAirplaneIcon className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">SaaS Agent</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="mt-6 px-4">
          <ul className="space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href || 
                (item.href !== '/' && location.pathname.startsWith(item.href));
              
              return (
                <li key={item.name}>
                  <NavLink
                    to={item.href}
                    className={clsx(
                      'flex items-center px-4 py-2.5 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    )}
                  >
                    <item.icon
                      className={clsx(
                        'mr-3 h-5 w-5',
                        isActive ? 'text-primary-600' : 'text-gray-400'
                      )}
                    />
                    {item.name}
                  </NavLink>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Company info */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
              <span className="text-primary-700 font-semibold">GO</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Genie Ops</p>
              <p className="text-xs text-gray-500">genie-ops.com</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        {/* Header */}
        <header className="sticky top-0 z-40 h-16 bg-white border-b border-gray-200 flex items-center px-8">
          <h1 className="text-lg font-semibold text-gray-900">
            SaaS Directory Submission Agent
          </h1>
        </header>

        {/* Page content */}
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
