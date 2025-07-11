import PropTypes from 'prop-types';

// project imports
import DrawerHeaderStyled from './DrawerHeaderStyled';
import Logo from 'components/logo';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';

// ==============================|| DRAWER HEADER ||============================== //

export default function DrawerHeader({ open }) {
  return (
    <DrawerHeaderStyled
      open={open}
      sx={{
        minHeight: '60px',
        width: 'initial',
        paddingTop: '8px',
        paddingBottom: '8px',
        paddingLeft: open ? '24px' : 0,
        backgroundColor: (theme) => theme.palette.sidebar.main,
      }}
    >
      <Stack direction="column" alignItems="flex-start">
        <Logo isIcon={!open} sx={{ width: open ? 'auto' : 35, height: 35 }} />
        <Typography variant="h6" color="white" sx={{ mt: 1 }}>
          Bank Indonesia Risk Scoring <br></br> & Early Detection System
        </Typography>
      </Stack>
    </DrawerHeaderStyled>
  );
}

DrawerHeader.propTypes = { open: PropTypes.bool };
