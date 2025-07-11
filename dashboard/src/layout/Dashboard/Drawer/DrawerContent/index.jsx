// project imports
import Navigation from './Navigation';
import SimpleBar from 'components/third-party/SimpleBar';
import { useGetMenuMaster } from 'api/menu';

// ==============================|| DRAWER CONTENT ||============================== //

export default function DrawerContent() {
  const { menuMaster } = useGetMenuMaster();

  return (
    <>
      <SimpleBar sx={{ 
        backgroundColor: (theme) => theme.palette.sidebar.main,
        height: '100vh',
        '& .simplebar-content': { display: 'flex', flexDirection: 'column', flex: 1  
        } }}>
        <Navigation />
        {/* {drawerOpen && <NavCard />} */}
      </SimpleBar>
    </>
  );
}
