import React, { useState, useRef } from 'react';
import { 
  CssBaseline, 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  CircularProgress, 
  Box, 
  Snackbar, 
  Switch, 
  FormControlLabel,
  IconButton
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import { Close as CloseIcon } from '@mui/icons-material';
import axios from 'axios';



const App = () => {
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [responseText, setResponseText] = useState('');
  const fileInputRef = useRef(null);
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem("darkMode") || prefersDarkMode || false
  );

  const theme = createTheme({
    palette: {
      primary: {
        main: "#21B0FE",
      },
      secondary: {
        main: '#D5A021',
      },
      action: {
        disabled: '#000',
        disabledBackground: '#535151',
      },
    },
  });

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0] instanceof Blob){
      setFile(e.target.files[0]);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(e.target.files[0]);
    }
  };

  const handleToggleDarkMode = () => {
    const toggledDarkMode = !darkMode
    localStorage.setItem('darkMode', toggledDarkMode)
    setDarkMode(toggledDarkMode);
  };

  const handleRemoveImage = () => {
    setFile(null);
    setImagePreview(null);
    fileInputRef.current.value = "";
  }

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('image', file);
    console.log(process.env.REACT_APP_API_URL)
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/process-receipt`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setSuccess(true);
      setResponseText(response.data);
    } catch (error) {
      setSuccess(false);
      console.error(error.response)
      setResponseText(error.response ? error.response.data : 'An error occurred');
    } finally {
      setLoading(false);
      handleRemoveImage()
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', backgroundColor: darkMode ? '#121212' : '#fff', color: darkMode ? '#fff' : '#000' }}>
        <AppBar position="sticky">
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>Receipt Scanner</Typography>
            <FormControlLabel
              control={<Switch color="secondary" checked={darkMode} onChange={handleToggleDarkMode} />}
              label="Dark Mode"
            />
          </Toolbar>
        </AppBar>

        <Box sx={{
          padding: 3,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          paddingTop: '16px',
        }}>
          <Typography variant="h4" gutterBottom>Receipt Upload</Typography>
          {imagePreview && (
            <Box mb={2}>
              <IconButton
                onClick={handleRemoveImage}
                sx={{
                  fontSize: '10px',
                  padding: '3px',
                  backgroundColor: '#696767',
                  '&:hover': {
                    backgroundColor: '#FF0000',
                  },
                }}
              >
                <CloseIcon sx={{  fontSize: '10px' }} />
              </IconButton>
              <img
                src={imagePreview}
                alt="Preview"
                style={{ width: '100%', maxHeight: '300px', objectFit: 'contain' }}
              />
            </Box>
          )}
          <Box sx={{
            padding: 3,
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            paddingTop: '16px',
          }}>
            <Button variant="contained" component="label" color="primary" sx={{ marginRight: 2 }}>
              Upload
              <input type="file" hidden onChange={handleFileChange}  ref={fileInputRef}/>
            </Button>

            <Button variant="contained" color="secondary" onClick={handleSubmit} disabled={loading || !file}>
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Submit'}
            </Button>
          </Box>
        </Box>

        <Snackbar
          open={success !== null}
          autoHideDuration={6000}
          onClose={() => setSuccess(null)}
          message={responseText}
          severity={success ? 'success' : 'error'}

        />
      </Box>
    </ThemeProvider>
  );
};

export default App;
