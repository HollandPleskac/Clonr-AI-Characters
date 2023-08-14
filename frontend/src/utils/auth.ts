export async function googleAuthorize() {
    try {
      const response = await fetch('http://localhost:8000/auth/google/authorize', {
        method: 'GET',
        headers: {
          'accept': 'application/json'
        }
      });
      const data = await response.json();
      console.log(data);
  
      // Assuming the authorization URL is in a field named 'authUrl'
      const authUrl = data.authUrl;
  
      // Redirect the user to the authorization URL
      window.location.href = authUrl;
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }
  
  
  
  