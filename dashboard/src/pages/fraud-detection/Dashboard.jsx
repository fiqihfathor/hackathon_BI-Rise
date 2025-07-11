// Required ENV: REACT_APP_POWERBI_URL
// Add REACT_APP_POWERBI_URL to your .env file in the dashboard project root

import Typography from '@mui/material/Typography';
import { height } from '@mui/system';
import MainCard from 'components/MainCard';

const POWERBI_URL = process.env.REACT_APP_POWERBI_URL;

export default function Dashboard() {
  if (!POWERBI_URL) {
    return (
      <MainCard sx={{ p: 4, m: 0, height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="h6" color="error">
          PowerBI URL is not set. Please define REACT_APP_POWERBI_URL in your .env file.
        </Typography>
      </MainCard>
    );
  }

  return (
    <MainCard sx={{ p: 0, m: 0, height: '100vh', overflow: 'hidden' }}>
      <iframe
        src={POWERBI_URL}
        title="Dashboard Iframe"
        style={{
          width: '100%',
          height: '100vh',
          border: 'none',
          display: 'block',
        }}
        allowFullScreen
      />
    </MainCard>
  );
}
