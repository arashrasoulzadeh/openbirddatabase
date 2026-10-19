import { API_URL } from './config';

/** "images/passeriformes/paridae/parus-major/1.jpg" -> the public URL the API serves it at. */
export const photoUrl = (file: string): string =>
  `${API_URL}/images/${file.replace(/^images\//, '').split('/').map(encodeURIComponent).join('/')}`;
