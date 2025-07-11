// assets
import AlertIcon from 'assets/images/nav-icon/Alerts.svg';
import DashboardIcon from 'assets/images/nav-icon/Dashboard.svg';
import RulesIcon from 'assets/images/nav-icon/Rules.svg';
import RISAIcon from 'assets/images/nav-icon/RISA.svg';

// ==============================|| MENU ITEMS - FRAUD DETECTION ||============================== //


const FraudDetection = {
  id: 'FraudDetection',
  title: 'Fraud Detection',
  type: 'group',
  children: [
    {
      id: 'fraudDetection-Alerts',
      title: 'Alerts',
      type: 'item',
      url: '/alerts',
      icon: AlertIcon
    },
    {
      id: 'fraudDetection-Rules',
      title: 'Rules',
      type: 'item',
      url: '/rules',
      icon: RulesIcon
    },
    {
      id: 'fraudDetection-Dashboard',
      title: 'Dashboard',
      type: 'item',
      url: '/dashboard',
      icon: DashboardIcon
    },
    {
      id: 'fraudDetection-RISA',
      title: 'RISA (Rise-Assistant)',
      type: 'item',
      url: '/risa',
      icon: RISAIcon
    }
  ]
};

export default FraudDetection;