export default function cookiesToString(cookies) {
    return cookies.map(cookie => `${cookie.name}=${cookie.value}`).join('; ');
}