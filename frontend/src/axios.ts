import axios from 'axios';

// Create an Axios instance with the base URL and other default settings
const instance = axios.create({
  baseURL: 'http://0.0.0.0:5006/',
  // You can add more default settings here
});

export default instance;