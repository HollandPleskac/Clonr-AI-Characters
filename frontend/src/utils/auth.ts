// import { redirect } from 'next/navigation'

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
    const authUrl = data.authorization_url;

    return authUrl
  } catch (error) {
    console.error('An error occurred:', error);
  }
}



