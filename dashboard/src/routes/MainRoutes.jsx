import { lazy } from 'react';

// project imports
import Loadable from 'components/Loadable';
import DashboardLayout from 'layout/Dashboard';

// render- Dashboard
const DashboardDefault = Loadable(lazy(() => import('pages/dashboard/default')));

// render - color
const Color = Loadable(lazy(() => import('pages/component-overview/color')));
const Typography = Loadable(lazy(() => import('pages/component-overview/typography')));
const Shadow = Loadable(lazy(() => import('pages/component-overview/shadows')));

// render - sample page
const SamplePage = Loadable(lazy(() => import('pages/extra-pages/sample-page')));

// render - fraud detection
const Alerts = Loadable(lazy(() => import('pages/fraud-detection/Alerts')));
const Rules = Loadable(lazy(() => import('pages/fraud-detection/Rules')));
const Dashboard = Loadable(lazy(() => import('pages/fraud-detection/Dashboard')));
const RISA = Loadable(lazy(() => import('pages/fraud-detection/Risa')));

// ==============================|| MAIN ROUTING ||============================== //

const MainRoutes = {
  path: '/',
  element: <DashboardLayout />,
  children: [
    {
      path: '/',
      children: [
        {
          path: 'alerts',
          element: <Alerts />
        },
        {
          path: 'rules',
          element: <Rules />
        },
        {
          path: 'dashboard',
          element: <Dashboard />
        },
        {
          path: 'risa',
          element: <RISA />
        }
      ]
    }
  ]
};

export default MainRoutes;
